$(function () {
    var code = $('.code').val();

    function showInviteText(data, status, xhr) {
        $('.invitee').html(data['invitee']);
        $('.invite-text').val(
            "Привет, " + data['invitee_name'] + "!\n" +
            "Чтобы поучаствовать в голосовании выпускников 57-ой " +
            "пройди по этой ссылке: http://auth.alumni57.ru/" + data['code'] + "\n" +
            "Это твоя персональная ссылка.\n\n" +
            data['inviter']
        );
        $('.invite').removeClass('hidden');
    }

    $(".alumni-select").autocomplete({
        source: "/api/get_alumni/",
        minLength: 2,
        select: function(event, ui) {
            $.ajax('/api/generate_code/', {
                data: {id: ui.item.id, code: code},
                success: showInviteText
            });
        }
    });
});