from unittest.mock import ANY, patch

import graphene

from .....checkout.error_codes import CheckoutErrorCode
from .....checkout.fetch import (
    fetch_checkout_info,
    fetch_checkout_lines,
    get_delivery_method_info,
)
from .....plugins.manager import get_plugins_manager
from ....tests.utils import get_graphql_content

MUTATION_UPDATE_SHIPPING_METHOD = """
    mutation checkoutShippingMethodUpdate(
            $checkoutId: ID, $token: UUID, $shippingMethodId: ID!){
        checkoutShippingMethodUpdate(
            checkoutId: $checkoutId,
            token: $token,
            shippingMethodId: $shippingMethodId
        ) {
            errors {
                field
                message
                code
            }
            checkout {
                id
                token
            }
        }
    }
"""


@patch("saleor.graphql.checkout.mutations.clean_shipping_method")
def test_checkout_shipping_method_update_by_id(
    mock_clean_shipping,
    staff_api_client,
    shipping_method,
    checkout_with_item,
):
    checkout = checkout_with_item
    old_shipping_method = checkout.shipping_method
    query = MUTATION_UPDATE_SHIPPING_METHOD
    mock_clean_shipping.return_value = True

    checkout_id = graphene.Node.to_global_id("Checkout", checkout.pk)
    method_id = graphene.Node.to_global_id("ShippingMethod", shipping_method.id)

    response = staff_api_client.post_graphql(
        query, {"checkoutId": checkout_id, "shippingMethodId": method_id}
    )
    data = get_graphql_content(response)["data"]["checkoutShippingMethodUpdate"]

    checkout.refresh_from_db()

    manager = get_plugins_manager()
    lines, _ = fetch_checkout_lines(checkout)
    checkout_info = fetch_checkout_info(checkout, lines, [], manager)
    checkout_info.delivery_method_info = get_delivery_method_info(
        old_shipping_method, checkout_info.shipping_address
    )
    checkout_info.shipping_method_channel_listings = None
    mock_clean_shipping.assert_called_once_with(
        checkout_info=checkout_info, lines=lines, method=ANY
    )
    errors = data["errors"]
    assert not errors
    assert data["checkout"]["id"] == checkout_id
    assert checkout.shipping_method == shipping_method


@patch("saleor.graphql.checkout.mutations.clean_shipping_method")
def test_checkout_shipping_method_update_by_token(
    mock_clean_shipping,
    staff_api_client,
    shipping_method,
    checkout_with_item,
):
    checkout = checkout_with_item
    old_shipping_method = checkout.shipping_method
    query = MUTATION_UPDATE_SHIPPING_METHOD
    mock_clean_shipping.return_value = True

    checkout_id = graphene.Node.to_global_id("Checkout", checkout.pk)
    method_id = graphene.Node.to_global_id("ShippingMethod", shipping_method.id)

    response = staff_api_client.post_graphql(
        query, {"checkoutId": checkout_id, "shippingMethodId": method_id}
    )
    data = get_graphql_content(response)["data"]["checkoutShippingMethodUpdate"]

    checkout.refresh_from_db()

    manager = get_plugins_manager()
    lines, _ = fetch_checkout_lines(checkout)
    checkout_info = fetch_checkout_info(checkout, lines, [], manager)
    checkout_info.delivery_method_info = get_delivery_method_info(old_shipping_method)
    checkout_info.shipping_method_channel_listings = None
    mock_clean_shipping.assert_called_once_with(
        checkout_info=checkout_info, lines=lines, method=ANY
    )
    errors = data["errors"]
    assert not errors
    assert data["checkout"]["id"] == checkout_id
    assert checkout.shipping_method == shipping_method


@patch("saleor.graphql.checkout.mutations.clean_shipping_method")
def test_checkout_shipping_method_update_neither_token_and_id_given(
    mock_clean_shipping, staff_api_client, checkout_with_item, shipping_method
):
    query = MUTATION_UPDATE_SHIPPING_METHOD
    mock_clean_shipping.return_value = True

    method_id = graphene.Node.to_global_id("ShippingMethod", shipping_method.id)

    response = staff_api_client.post_graphql(query, {"shippingMethodId": method_id})
    data = get_graphql_content(response)["data"]["checkoutShippingMethodUpdate"]
    assert len(data["errors"]) == 1
    assert not data["checkout"]
    assert data["errors"][0]["code"] == CheckoutErrorCode.GRAPHQL_ERROR.name


@patch("saleor.graphql.checkout.mutations.clean_shipping_method")
def test_checkout_shipping_method_update_both_token_and_id_given(
    mock_clean_shipping, staff_api_client, checkout_with_item, shipping_method
):
    checkout = checkout_with_item
    query = MUTATION_UPDATE_SHIPPING_METHOD
    mock_clean_shipping.return_value = True

    checkout_id = graphene.Node.to_global_id("Checkout", checkout.pk)
    method_id = graphene.Node.to_global_id("ShippingMethod", shipping_method.id)

    response = staff_api_client.post_graphql(
        query,
        {
            "checkoutId": checkout_id,
            "token": checkout_with_item.token,
            "shippingMethodId": method_id,
        },
    )
    data = get_graphql_content(response)["data"]["checkoutShippingMethodUpdate"]

    assert len(data["errors"]) == 1
    assert not data["checkout"]
    assert data["errors"][0]["code"] == CheckoutErrorCode.GRAPHQL_ERROR.name
