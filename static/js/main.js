$(document).ready(function() {
    $('button.up-vote').click(function() {
        var songId = $(this).data("songId");
        $.ajax("/songs/"+songId, {data: {vote: "up"}, method: "PATCH"}).done(function (data) {
            console.log(data);
            $(".points." + songId).html(data["points"])
        });

    });

    $('button.down-vote').click(function() {
        var songId = $(this).data("songId");
        $.ajax("/songs/"+songId, {data: {vote: "down"}, method: "PATCH"}).done(function (data) {
            console.log(data);
            $(".points." + songId).html(data["points"])
        });
    });
});