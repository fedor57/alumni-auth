function getIntCookie(name, def)
{
    var val = Cookies.get(name);
    if (about === undefined)
        return def;
    val = parseInt(val, 10);
    if (isNaN(val))
        return def;
    return val;
}

$(document).ready(function () {
    if (window.location.hash.length > 0) {
        var input = $('.code-input');
        if (input.length) {
            input.val(window.location.hash.substr(1));
            window.location.hash = '';
        }
    }


    var about = getIntCookie('about', 1);

    if (about < 1)
    {
        $("#about").addClass('hidden');
        $("#what-is-this").removeClass('hidden');
    }
    $("#about").click(function (e) {
        $(this).addClass('hidden');
        $("#what-is-this").removeClass('hidden');
        Cookies.set('about', 0, { expires: 31 });
    });
    $("#what-is-this").click(function (e) {
        $(this).addClass('hidden');
        $("#about").removeClass('hidden');
        Cookies.set('about', 1, { expires: 31 });
    });

    $(".alumni-select").autocomplete({
        source: "/api/get_alumni/",
        minLength: 2,
        select: function (event, ui) {
            $('.invitee-id').val(ui.item.id);
            $('.invite-button').removeAttr('disabled');
        }
    });

    $("#create-own-code").popover({
        trigger: 'hover',
        placement: 'right'
    });
    $("#this-is-important").popover({
        trigger: 'hover',
        placement: 'right'
    });
    $(".disable-code-link").popover({
        trigger: 'hover',
        placement: 'right',
    });
    $(".input-code-link").popover({
        trigger: 'hover',
        placement: 'right',
    });
    $("#input-code-form").hide();
    $(".input-code-link").click(function () {
        $("#input-code-form").show();
        $("#input-code-box").focus();
    });


    $('.disable-code-link').click(function(e) {
        if (!window.confirm('Убедитесь, что у вас записан другой работающий код. Отключенный код нельзя включить обратно. Отключить код?')) {
            e.preventDefault();
            return false;
        }
    });
});
