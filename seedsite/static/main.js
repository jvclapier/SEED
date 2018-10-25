
$('.card-body').click(function() {
    console.log('card flip function called');
    $(this).closest('.card-flip').toggleClass('hover');
    $(this).css('transform, rotateY(180deg)');
});

$( '#bottom-navbar .nav-link i' ).on( 'click', function () {
	$( '#bottom-navbar .nav-link' ).find( 'i.active' ).removeClass( 'active' );
	$( this ).addClass( 'active' );
});

var setDefaultActive = function() {
    var currentPage = $(".where-am-i").text();
    var selectedTab = $('.' + currentPage);

    console.log(selectedTab.text());

    selectedTab.addClass('active');
}

setDefaultActive()
