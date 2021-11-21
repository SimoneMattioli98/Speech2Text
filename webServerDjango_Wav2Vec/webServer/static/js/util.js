const input_check = document.getElementById('id_request_check');

const audio_form = document.getElementById("audio_form").reset();

function submit_reset(){
    audio_form.submit()
    audio_form.reset()
}

function check() {
    window.location = '/checkrequest/'+input_check.value
}

function back(){
    window.location = '/'
}