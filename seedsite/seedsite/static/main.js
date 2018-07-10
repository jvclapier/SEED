$('.card-body').click(function() {
    console.log('card flip function called');
    $(this).closest('.card-flip').toggleClass('hover');
    $(this).css('transform, rotateY(180deg)');
});
