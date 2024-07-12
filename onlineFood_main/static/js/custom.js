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
                if(response.status == 'Failed'){
                    console.log('raise the error message')
                }else{
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
                if(response.status == 'Failed'){
                    console.log('raise the error message')
                }else{
                    $('#cart-counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                }
            }

        })
    })

});