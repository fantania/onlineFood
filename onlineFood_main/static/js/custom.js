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
                    removeCartItem(0, cart_id)  
                }
            }
        })
    })

    // Delete the cart item if the quantity is 0
    function removeCartItem(cartItemQty, cart_id){
        if(cartItemQty <= 0){
            //remove the item element
            //$('#cart-item-'+cart_id).remove()
            document.getElementById("cart-item-"+cart_id).remove()
        }
    }
});