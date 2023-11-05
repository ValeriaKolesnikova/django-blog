console.log('sing-up')
$(function () {
  $('#signUpForm').submit(singUp);
});

function singUp(e) {
  let form = $(this);
  e.preventDefault();
  $.ajax({
    url: '/api/v1/auth/sign-up/',
    type: 'post',
    data: form.serialize(),
    success: singUpSuccessHandler,
    error: singUpErrorHandler,
  })
  console.log('here')
}

function singUpSuccessHandler(data) {
  console.log('success', data)
}

function singUpErrorHandler(data) {
  console.log('error', data)
}