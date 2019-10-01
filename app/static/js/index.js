
$(document).ready(function(){
    console.log("here");
    $("#mainPost").css({"background-size": "100%"});
}); 

$(function() {
    console.log("postPic");
    $('#fbId').width(100);
    $('#fbId').height(25);
});

$(function() {
    console.log("postPic");
    $('#twId').width(100);
    $('#twId').height(25);
});

function changeSign(signStr) {
    document.getElementById("signin-btn").innerHTML = signStr;
}

$("#signin").submit(function(e) {
    var email = $('input[name="emailid"]').val();
    var password = $('input[name="password"]').val();

    if (email == '' || password == '') {
        alert("Username and Password should not be empty");
        return;
    }

    $.ajax({
        url: $SCRIPT_ROOT + "/auth/login",
        data: JSON.stringify({ emailid: email, password: password}),
        method: "POST",
        datatype: 'json',
        contentType: "application/json; charset=utf-8"
    })
    .done(function(data, status ) {
        alert('login successful');
        changeSign('Sign Out');
        //$('#SigninModal').modal('toggle');
    }).fail(function(data, status) {
        alert('login failed');
        //$('#SigninModal').modal('toggle');
    });
});

    $("#register").submit(function(e) {
        var email = $('input[name="remailid"]').val();
        var password = $('input[name="rpassword"]').val();
        var cpassword = $('input[name="rcpassword"]').val();

        if (email == '' || password == '' || cpassword == '') {
            alert("Username and Password should not be empty");
            return;
        }

        $.ajax({
            url: $SCRIPT_ROOT + "/auth/register",
            data: JSON.stringify({ emailid: email, password: password, cpassword: cpassword}),
            method: "POST",
            datatype: 'json',
            contentType: "application/json; charset=utf-8"
        })
        .done(function(data, status ) {
            $('#RegisterModal').modal('toggle');
        }).fail(function(data, status) {
            $('#RegisterModal').modal('toggle');
        });
    });
