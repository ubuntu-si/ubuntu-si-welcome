
# Add scripts to load to this array. These can be loaded remotely like jquery
# is below, or can use file paths, like 'vendor/underscore'

pat= if document.location.pathname.length>2 then document.location.pathname.replace /index.html/,"" else ""
js = [
  "jquery"
  "#{pat}/js/director.js"
]

class UbuntuSI
  ## Predloge
  render_menu:(name, url)->
    "<a id=\"#{url}\" href=\"/slug/#{url}\"><h2>#{name}</h2></a>"

  constructor: (@url) ->
    @menu = $("aside")
    @vsebina = $("section")

    page("/slug/:id", @odpri)

    $.ajaxSetup({
      error: (xhr, status, error) =>
        @url = "#{pat}/js/offline.json"
        unless xhr.status == 404
          setTimeout ()=>
            jQuery.getJSON @url, @parse
          ,5000
    })

    unless navigator.onLine
      @url = "#{pat}/js/offline.json"

    @pages = sessionStorage["cache"]
    unless @pages
      jQuery.getJSON @url, @parse
    else
      @pages = JSON.parse sessionStorage["cache"] 
      @render()

  parse:(data)=>
    if data.status != null
      @pages = data.page.children
      sessionStorage["cache"] = JSON.stringify @pages
      @render()
  render:()=>
    for wpage in @pages
      @menu.append $(@render_menu wpage.title, wpage.slug)

    page("/slug/#{@pages[0].slug}")

    @menu.find("a").on "click", ()->
      page($(this).attr "href")
      false

    $("body").removeClass "loading"
  odpri:(data)=>
    slug = data.params["id"]
    @vsebina.html @najdi slug
    tocno = $("a##{slug}")
    if tocno.length
      @menu.find("a").removeClass "izbrano"
      tocno.addClass "izbrano"
  najdi:(slug)=>
    for wpage in @pages
      if wpage.slug == slug
        return wpage.content
      
    
# this will fire once the required scripts have been loaded
require js, ->
  $ ->
    new UbuntuSI "https://www.ubuntu.si/welcome-app/?json=1&children=1"