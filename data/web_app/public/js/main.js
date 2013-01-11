(function() {
  var js, pat;

  pat = document.location.pathname.length > 2 ? document.location.pathname : "";

  js = ["jquery", "" + pat + "/js/director.js"];

  require(js, function() {
    return $(function() {
      return console.log("@");
    });
  });

}).call(this);
