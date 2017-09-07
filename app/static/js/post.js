var id = 1;

function addElement(comment_in_json) {
    var id = 1;
    console.log('grunt working');
    var main_div_elem = $('<div />', {id : 'main_div_elem'.concat(id), "class" : "row"});
    
    var col_md_8_elem = $('<div />', {id : 'col_md_8_elem'.concat(id), "class" : "col-md-8"});
    main_div_elem.append(col_md_8_elem);  
    var media_elem = $('<div />', {id : 'media_elem'.concat(id), "class" : "media"});
    $(col_md_8_elem).append(media_elem);
    var media_left_top_elem = $('<div />', {id : 'media_left_top_elem'.concat(id), "class" : "media-left media-top"});
    $(media_elem).append(media_left_top_elem);

    var img_media_elem = $('<img>', {id : 'img_media_elem'.concat(id), "class": "media-object", 
                                     src : comment_in_json['pfl_pic'],
                                     css : {width : "60px"}}); 
    $(media_left_top_elem).append(img_media_elem);                                       


    var media_body_elem = $('<div />', {id : 'media_body_elem'.concat(id), "class" : "media-body"});    
    var h4_body_elem = $('<div />', {id : 'h4_body_elem'.concat(id), "class" : "media-heading"});
    $(media_body_elem).append(h4_body_elem);
    
    console.log("EVAL");
    console.log(eval(comment_in_json['is_anon']));
    var strong_elem = $('<strong />', {id : 'strong_elem'.concat(id), text : comment_in_json['uname'],                                           
                                       css : {color : 'black', fontSize : "18px"}});
    var time_elem = $('<h4 />', {id : 'time_elem'.concat(id), 
                                 css : {fontSize : "14px", color: "black"},
                                 text : moment(comment_in_json['ts']).fromNow(refresh = true)});
    $(h4_body_elem).append(strong_elem, time_elem);

    var p_comment_elem = $('<p />', {id : 'p_comment_elem'.concat(id)});
    
    var h4_comment_elem = $('<h4 />', {id : 'h4_comment_elem'.concat(id), 
                                       "class" : "blog-comment",
                                       text : comment_in_json['comment']});
    $(p_comment_elem).append(h4_comment_elem);
    $(media_elem).append(media_body_elem);
    $(media_body_elem).append(p_comment_elem);
    if (comment_in_json['is_anon'] === 1) {
        $('#div'.concat(id)).append(main_div_elem);
    } else {
        $('#div'.concat(id)).append(main_div_elem);        
    }    

    var children = document.getElementById("div1").childNodes;
    console.log(children);
}

$(function() { 
    $('#submitWithName').click(function() {
        var uname = $('input[name="uname"]').val();
        var comment = $('textarea[name="comment"]').val();

        console.log(uname);
        console.log("Comment14");
        $.ajax({
            url: $SCRIPT_ROOT + "/submit_comment",
            data: JSON.stringify({ name: uname, comment: comment, post_id: post_id }),
            method: "POST",
            datatype: 'json',
            contentType: "application/json; charset=utf-8"
        })
        .done(function(data, status ) {
            console.log('Where');
            console.log(JSON.stringify(data));            
            addElement(data);
            $('#textIdwithOutUser').val('');
            $('#inputId').val('');
        }).fail(function(data, status) {
            console.log(status);
            console.log(JSON.stringify(data));
        });
    });
});

$(function() { 
    $('#submitWithOutName').click(function() {
        var comment = $('textarea[name="comment"]').val();

        console.log(comment);
        console.log("Comment14");
        $.ajax({
            url: $SCRIPT_ROOT + "/submit_comment",
            data: JSON.stringify({ comment: comment, post_id: post_id }),
            method: "POST",
            datatype: 'json',
            contentType: "application/json; charset=utf-8"
        })
        .done(function(data, status ) {
            console.log('Where');
            console.log(JSON.stringify(data));            
            addElement(data);
            $('#textIdwithUser').val('');
        }).fail(function(data, status) {
            console.log(status);
            console.log(JSON.stringify(data));
        });
    });
});

$(function() {
    console.log("postPic");
    $("#postPic").attr("src", post_pic_url);
    $('#postPic').width(1000);
    $('#postPic').height(550);
});

$(function() {
    console.log("postPic");
    $('#fbId').width(200);
    $('#fbId').height(25);
});

$(function() {
    console.log("postPic");
    $('#twId').width(200);
    $('#twId').height(25);
});

function withoutUsercheck() {
    console.log("Reached");
    var txtvalue=$.trim($("#textIdwithOutUser").val());
    var nameValue=$.trim($("#inputId").val());
    if(txtValue > 0 && nameValue > 0) {
      $("#submitWithName").prop('disabled', false);
    } else {
      $("#submitWithName").prop('disabled', true);
    }
}

function withUsercheck() {
    console.log("Reached 1");
    var txtvalue=$.trim($("#textIdwithUser").val());
    if(txtValue > 0) {
      $("#submitWithOutName").prop('disabled', false);
    } else {
      $("#submitWithOutName").prop('disabled', true);
    }
}

function fbs_click(post_url, post_header) {
    console.log(post_url);
    console.log(post_header);
    var twtTitle = document.title;
    var twtUrl = post_url;
    var dataSize = "large";
    var dataText=post_header;
    var dataHashtags = "football, football_tactics";
    var dataVia = "footynotes1"
    var maxLength = 140 - (twtUrl.length + 1);
    if (twtTitle.length > maxLength) {
        twtTitle = twtTitle.substr(0, (maxLength - 3)) + '...';
    }
    var twtLink = 'http://twitter.com/share?url=' + encodeURIComponent(twtUrl) + "&text=" + encodeURIComponent(dataText) +  "&hashtags=" + encodeURIComponent(dataHashtags) + "&via=" +encodeURIComponent(dataVia);
    window.open(twtLink);
}

