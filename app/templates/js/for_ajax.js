var div_id = 1;


function addElement(name, is_anon, comment) {
    var id = "";

    // div element for row.
    console.log(name); 
    var rowDiv = document.createElement('div');
    rowDiv.classList.add("row");

    // div element for col.
    var colDiv = document.createElement('div');
    colDiv.classList.add("col-md-8"); 

    // col append to row.
    rowDiv.appendChild(colDiv);

    // div element for media.
    var mediaDiv = document.createElement('div');
    mediaDiv.classList.add("media"); 

    // col append to row.
    colDiv.appendChild(mediaDiv);

    // div element for media-left and media-top.
    var mediaLeft_And_Top_Div = document.createElement('div');
    mediaLeft_And_Top_Div.classList.add("media-left"); 
    mediaLeft_And_Top_Div.classList.add("media-top"); 

    // media-let and media-top append to mediaDiv.
    mediaDiv.appendChild(mediaLeft_And_Top_Div);

    // div element for media-body.
    var mediaBody = document.createElement('div');
    mediaBody.classList.add("media-body"); 

    // col append to row.
    mediaDiv.appendChild(mediaBody);

    // div element for media-left and media-top.
    var mediaObj_Img = document.createElement('img');
    mediaObj_Img.classList.add("media-object"); 
    mediaObj_Img.src = '../static/tactification.jpg';
    mediaObj_Img.style.width = "60px";

    if (is_anon === 1) {
        // img append to left_and_top.
        mediaLeft_And_Top_Div.appendChild(mediaObj_Img);
    } else {
        var a_Obj = document.createElement('a');
        a_Obj.href = 'http://www.google.co.in';
        mediaLeft_And_Top_Div.appendChild(a_Obj);
        a_Obj.appendChild(mediaObj_Img);
    }

    // h4 for media-heading
    var mediaHeading = document.createElement('h4');
    mediaHeading.classList.add("media-heading"); 

    // heading append to body.
    mediaBody.appendChild(mediaHeading);

    if (is_anon === 1) {
        // strong for username 
        var strongElem = document.createElement('strong');
        strongElem.innerHTML = name; 

        // heading append to body.
        mediaHeading.appendChild(strongElem);
    } else {
        var a_Obj_1 = document.createElement('a');
        a_Obj_1.href = 'http://www.facebook.com';
        a_Obj_1.innerHTML = name;
        mediaHeading.appendChild(a_Obj_1);
    }
    
    // p for blog-comment 
    var commentDiv = document.createElement('p');
    mediaBody.appendChild(commentDiv);
    
    // h4 for blog-comment 
    var h4Div = document.createElement('h4');
    h4Div.classList.add("blog-comment"); 
    h4Div.innerHTML = comment;
    commentDiv.appendChild(h4Div);

    // h4 for media-bottom 
    var mediaBottom_Div = document.createElement('h4');
    mediaBottom_Div.classList.add("media-bottom"); 
    mediaBody.appendChild(mediaBottom_Div);

    // span under media-bottom
    var spanMediaBottom_Div = document.createElement('span');
    mediaBottom_Div.appendChild(spanMediaBottom_Div);    

    // row under span under media-bottom
    var row_Span_mediaBottom_Div = document.createElement('div');
    row_Span_mediaBottom_Div.classList.add('row');
    spanMediaBottom_Div.appendChild(row_Span_mediaBottom_Div);

    // offset col under row under span under media-bottom
    var off_col_row_span_mediaBottom_Div = document.createElement('div');
    off_col_row_span_mediaBottom_Div.classList.add('col-lg-9', 'col-md-9', 'col-sm-9', 'col-xs-9');
    row_Span_mediaBottom_Div.appendChild(off_col_row_span_mediaBottom_Div);

    // col under row under span under media-bottom
    var col_row_span_mediaBottom_Div = document.createElement('div');
    col_row_span_mediaBottom_Div.classList.add('col-lg-3', 'col-md-3', 'col-sm-3', 'col-xs-3');
    row_Span_mediaBottom_Div.appendChild(col_row_span_mediaBottom_Div);

    // a under col under row under span under media-bottom
    var a_col_row_span_mediaBottom_Div = document.createElement('a');
    a_col_row_span_mediaBottom_Div.href = 'del_url';
    a_col_row_span_mediaBottom_Div.innerHTML = 'Delete';
    col_row_span_mediaBottom_Div.appendChild(a_col_row_span_mediaBottom_Div);

    // col under row under span under media-bottom 
    console.log(name); 

    id.concat("div" + div_id); 
    console.log(id);

    var currentDiv = document.getElementById("div1");
    document.body.insertBefore(rowDiv, currentDiv);
    div_id = div_id+1;
} 
