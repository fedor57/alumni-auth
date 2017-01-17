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
    var about = getIntCookie('about', 1);

    if (about < 1)
    {
        $("#about").addClass('hidden');
        $("#what-is-this").removeClass('hidden');
    }
    $("#about").click(function (e) {
        $(this).addClass('hidden');
        $("#what-is-this").removeClass('hidden');
        Cookies.set('about', 0);
    });
    $("#what-is-this").click(function (e) {
        $(this).addClass('hidden');
        $("#about").removeClass('hidden');
        Cookies.set('about', 1);
    });

    $(".alumni-select").autocomplete({
        source: "/api/get_alumni/",
        minLength: 2,
        select: function (event, ui) {
            $('.invitee-id').val(ui.item.id);
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
});
