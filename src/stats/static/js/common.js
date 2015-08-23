function tours_uri() {
    var base_uri = new URI(window.location);
    $('.nav_tour_items a').each(function () {
        base_uri.removeSearch('tour');
        var tour_id = $(this).attr('href').split('=')[1];
        var tour_uri = base_uri.addSearch('tour', tour_id);
        $(this).prop('href', tour_uri.search());
    });
}


$(document).ready(function () {
    var base_uri = new URI(window.location);
    $('.nav_menu a').each(function () {
        var link_uri = new URI($(this).attr('href'));
        if (base_uri.normalizePath().path() === link_uri.normalizePath().path()) {
            $(this).addClass('active');
        }
    });
    $('.nav_tabs a').each(function () {
        var link_uri = new URI($(this).attr('href'));
        if (base_uri.normalizePath().path() === link_uri.normalizePath().path()) {
            $(this).addClass('active');
        }
    });
    tours_uri();

    $('.message .close').click(function () {
        $(this).parent().hide();
    });

});
