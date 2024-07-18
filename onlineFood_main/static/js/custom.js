$(document).ready(function(){

    // add cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if(response.status == 'login_required'){
                    Swal.fire({
                        icon: "info",
                        text: response.message
                      }).then(function(){
                        window.location = '/login'
                      });
                }if(response.status == 'Failed'){
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: response.message
                      });
                }
                else{
                    $('#cart-counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    // subtotal, tax, delivery, transaction and grand totat
                    applyCartAmounts(
                        response.cart_amount['subtotal'], 
                        response.cart_amount['tax'], 
                        response.cart_amount['transaction'], 
                        response.cart_amount['delivery'], 
                        response.cart_amount['grand_total']
                    )
                }
            }

        })
    })

    //Place the cart item quantity on load
    $('.item-qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $('#'+the_id).html(qty)

    })


    // decrease cart
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();

        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if(response.status == 'login_required'){
                    Swal.fire({
                        icon: "info",
                        text: response.message
                      }).then(function(){
                        window.location = '/login'
                      });
                }if(response.status == 'Failed'){
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: response.message
                      });
                }
                else{
                    $('#cart-counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                    removeCartItem(response.qty, cart_id);
                    checkEmptyCart(); 
                    // subtotal, tax, delivery, transaction and grand totat
                    applyCartAmounts(
                        response.cart_amount['subtotal'], 
                        response.cart_amount['tax'], 
                        response.cart_amount['transaction'], 
                        response.cart_amount['delivery'], 
                        response.cart_amount['grand_total']
                    )
                }
            }
        })
    })

    //Delete cart item
    $('.delete_cart').on('click', function(e){
        e.preventDefault();
        
        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){if(response.status == 'Failed'){
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: response.message
                      });
                }
                else{
                    $('#cart-counter').html(response.cart_counter['cart_count']);
                    Swal.fire({
                        icon:response.status,
                        title: "Great...",
                        text: response.message
                      });   
                    removeCartItem(0,cart_id);
                    checkEmptyCart(); 
                    // subtotal, tax, delivery, transaction and grand totat
                    applyCartAmounts(
                        response.cart_amount['subtotal'], 
                        response.cart_amount['tax'], 
                        response.cart_amount['transaction'], 
                        response.cart_amount['delivery'], 
                        response.cart_amount['grand_total']
                    )
                }
            }
        })
    })

    // Delete the cart item if the quantity is 0
    function removeCartItem(cartItemQty, cart_id){
        if(cartItemQty <= 0){
            var cartItemElement = document.getElementById("cart-item-" + cart_id);
            if (cartItemElement) {
                document.getElementById("cart-item-" + cart_id).remove();
            } else {
                console.error("Element with ID 'cart-item-" + cart_id + "' not found.");
            }
        }
    }

    //Check if the cart is empty
    function checkEmptyCart(){
        var cart_counter = $('#cart-counter').html()
        if(cart_counter == 0){
            $('#empty-cart').css("display", "block");
        }
    }

    //apply cart amounts
    function applyCartAmounts(subtotal, tax, transaction, delivery, grand_total){
        if(window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal)
            $('#tax').html(tax)
            $('#transaction').html(transaction)
            $('#delivery').html(delivery)
            $('#total').html(grand_total)
        }
    
    }
});