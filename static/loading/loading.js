// Enable pusher logging - don't include this in production
    Pusher.logToConsole = true;

    var pusher = new Pusher('33726bd9f5b34f01cc85', {
      encrypted: true
    });

    var channel = pusher.subscribe('my-channel');
    channel.bind('my-event', function(data) {
      alert(data.message);
    });
