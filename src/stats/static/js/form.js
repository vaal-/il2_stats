$(document).ready(function () {
    $('input[type="password"]').each(function () {
        $(this).after('<div class="password_wink"></div>');
        $(this).parent().find('input').prop('type', 'text');
    });

    $('.password_wink').click(function () {
        if ($(this).hasClass('password_wink_hide')) {
            $(this).removeClass('password_wink_hide');
            $(this).parent().find('input').prop('type', 'text');
        } else {
            $(this).addClass('password_wink_hide');
            $(this).parent().find('input').prop('type', 'password');
        }
    });
});
