console.log('hello')
$(function () {
    verifyEmail()
  });

function verifyEmail () {
    const urlParams = new URLSearchParams (window.location.search)
    const data = {
        "key": urlParams.get('key')
      }
    $.ajax({
        url: '/api/v1/auth/sign-up/verify/',
        type: 'post',
        data: data,
        success: confirmSuccessHandler,
        error: confirmErrorHandler,
    })
}

function confirmSuccessHandler(data) {
    console.log('success', data);
    window.location.assign('/login/'); 
  }
  
  function confirmErrorHandler(data) {
    console.log('error', data)
  }