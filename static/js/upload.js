var file, response;
var xhr = new XMLHttpRequest();
var put_xhr = new XMLHttpRequest();
var finish_xhr = new XMLHttpRequest();
var trigger_xhr = new XMLHttpRequest();

function startUpload() {
    var replacement = '<div class="progress"><div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="45" aria-valuemin="0" aria-valuemax="100" style="width: 45%"></div></div>';
    $("#infotext").replaceWith('<div id="upload_form">' + replacement + '</div>');

    var datatype = document.getElementById('upload_datatype').value;
    if (!datatype) {
        alert("Please select a datatype");
        return;
    }
    var description = document.getElementById('upload_description').value;
    var metadata = {'tags': [],
                    'description': description};
    uploadFile(JSON.stringify([datatype]), JSON.stringify(metadata));
};


function uploadFile(datatypes, metadata) {
    var files = document.getElementById('upload_file').files;
    if (!files.length) {
        return;
    }
    file = files[0];
    url = oh_direct_upload_url+"?access_token="+access_token;
    console.log(url);
    xhr.open('POST', url, true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send('project_member_id='+member_id+'&datatypes='+datatypes+'&filename='+file.name+'&metadata='+metadata);
    xhr.onreadystatechange = putFile;
}

function putFile(e) {
  if (xhr.readyState === 4 && xhr.status === 201) {
    response = JSON.parse(xhr.responseText);
    put_xhr.open('PUT', response.url, true);
    put_xhr.setRequestHeader('Content-type','');
    put_xhr.responseType = 'text';
    put_xhr.send(file);
    put_xhr.onreadystatechange = uploadedFile;
  } else {
    console.log('checking status of upload url XHR');
  }
}

function uploadedFile(e) {
  if (put_xhr.readyState === 4 && put_xhr.status === 200) {
    finish_xhr.open('POST', oh_direct_upload_complete_url+"?access_token="+access_token, true);
    finish_xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    finish_xhr.send('project_member_id='+member_id+'&file_id='+response.id);
    finish_xhr.onreadystatechange = finishedFile;
  } else {
    console.log('checking status of upload XHR');
  }
}

function finishedFile(e) {
      if (finish_xhr.readyState === 4 && finish_xhr.status === 200) {
        console.log('uploaded file');
        console.log(response);
        trigger_xhr.open('POST', "/trigger_processing/", true);
        trigger_xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        trigger_xhr.send('access_token='+access_token+'&file_id='+response.id+'&csrfmiddlewaretoken='+csrf_token);
        var done = "<h3>Upload successful.</h3>";
        $("#upload_form").replaceWith('<div id="upload_form">'+done+'</div>');
      } else {
        console.log('checking status of finalizing XHR');
      }
    }
