

function scoring () {
    $('.right.score').each(function () {
        var values = $(this).html().split('×');
        var total = values[0].trim() * values[1].trim();
        $(this).append(' = <span class="sum">' + total + '</span>');
    });
}
