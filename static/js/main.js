$(document).ready(function() {
    $('button.up-vote').click(function() {
        console.log(this);
        //$.post('/songs/', param1: 'value1', function(data) {
        //});
    })

    $('button.down-vote').click(function() {
        console.log(this);
        //$.post('/path/to/file', param1: 'value1', function(data) {
            /*optional stuff to do after success */
        //});
    })
});