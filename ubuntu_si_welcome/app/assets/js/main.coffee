
# Add scripts to load to this array. These can be loaded remotely like jquery
# is below, or can use file paths, like 'vendor/underscore'

pat= if document.location.pathname.length>2 then document.location.pathname else ""
js = [
  "jquery"
  "#{pat}/js/director.js"
]

# this will fire once the required scripts have been loaded
require js, ->
  $ ->
    console.log "@"