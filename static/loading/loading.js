var api_url = '/final?uid='
// Enable pusher logging - don't include this in production
Pusher.logToConsole = true;
var pusher = new Pusher('33726bd9f5b34f01cc85', {
  encrypted: true
});

var app = new Vue({
  el: '#app',
  data: {
    progress: 0,
    message: 'Waiting...'
  },
  watch: {
    progress: function(curr_progress) {
      if (curr_progress == 100) {
        window.location.href = api_url + user_name
      }
    }
  }
})
console.log(user_name)
var channel = pusher.subscribe('user_instantiate_' + user_name);
channel.bind('update', function(data) {
  Vue.set(app, 'progress', Math.round(data.progress))
  Vue.set(app, 'message', data.message)
});
