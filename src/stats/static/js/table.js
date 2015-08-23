

function uri_sort_by(sort_by_default, sort_by_text) {
    var base_uri = new URI(window.location);
    var query = base_uri.search(true);
    //var current_sort_by = '-rating';
    var current_sort_by = sort_by_default;
    if ('sort_by' in query) {
        if (typeof query['sort_by'] === 'string') {
            current_sort_by = query['sort_by'];
        } else {
            // если параметров несколько используем последний
            current_sort_by = query['sort_by'][query['sort_by'].length - 1];
        }
        base_uri.removeSearch('sort_by');
    }

    var current_sort_by_dir = 'asc';
    if (current_sort_by.slice(0, 1) === '-') {
        current_sort_by_dir = 'desc';
        current_sort_by = current_sort_by.replace('-', '');
    }
    if (sort_by_text) {
        $('#sort_by_text').text(sort_by_text[current_sort_by]);
    }

    $('a.sort_by').each(function () {
        var def_sort_by = $(this).attr('href').split('=')[1];
        var def_sort_by_dir = 'asc';
        if (def_sort_by.slice(0, 1) === '-') {
            def_sort_by_dir = 'desc';
            def_sort_by = def_sort_by.replace('-', '');
        }

        var new_sort_by = def_sort_by;
        if (current_sort_by === def_sort_by) {
            if (current_sort_by_dir === 'desc') {
                $(this).addClass('sort_by_desc');
            } else {
                $(this).addClass('sort_by_asc');
                new_sort_by = '-' + def_sort_by;
            }
        } else {
            if (def_sort_by_dir === 'desc') {
                new_sort_by = '-' + def_sort_by;
            }
        }

        $(this).attr('href', base_uri.addSearch('sort_by', new_sort_by));
        base_uri.removeSearch('sort_by');
    });
}

$(document).ready(function() {
    //$('tr[data-href] td').each(function () {
    //    $(this).css('padding-top', 0);
    //    $(this).css('padding-bottom', 0);
    //    var new_html = '<a href="' + $(this).parent().data('href') + '">' + $(this).html() + '</a>';
    //    $(this).html(new_html);
    //});
});
