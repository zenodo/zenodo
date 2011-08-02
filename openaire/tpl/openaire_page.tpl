<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-gb" lang="en-gb" dir="ltr">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <meta http-equiv="x-ua-compatible" content="IE=EmulateIE7" />
  <meta name="robots" content="index, follow" />
  <meta name="keywords" content="Open Access, repository, repositories, deposit publication, Open Access Europe, Open Research Data, Repository Usage statistics, Invenio, CERN" />
  <meta name="title" content="%(title)s" />
  <meta name="author" content="Administrator" />
  <meta name="description" content="OpenAIRE - Open Access Infrastructure Research for Europe" />
  <meta name="generator" content="%(release)s" />
  <title>OpenAIRE Orphan Repository - %(title)s</title>
    %(headers)s
  <link href="%(portalurl)s/templates/yoo_level/favicon.ico" rel="shortcut icon" type="image/x-icon" />
  <link rel="stylesheet" href="%(portalurl)s/administrator/components/com_twitter/assets/css/jlord_core.css" type="text/css" />
  <link rel="stylesheet" href="%(portalurl)s/media/system/css/modal.css" type="text/css" />
  <link rel="stylesheet" href="%(portalurl)s/templates/yoo_level/css/template.css" type="text/css" />
  <link rel="stylesheet" href="%(portalurl)s/templates/yoo_level/css/openaire2/openaire2-layout.css" type="text/css" />
  <link rel="stylesheet" href="%(portalurl)s/templates/yoo_level/css/custom.css" type="text/css" />
  <link rel="stylesheet" href="%(portalurl)s/modules/mod_yoo_login/mod_yoo_login.css.php" type="text/css" />
  <link rel="stylesheet" href="%(portalurl)s/modules/mod_yoo_search/mod_yoo_search.css.php" type="text/css" />
  <link rel="stylesheet" href="%(portalurl)s/modules/mod_jflanguageselection/tmpl/mod_jflanguageselection.css" type="text/css" />
  <style type="text/css">
    <!--
div.wrapper { width: 960px; }
    -->
  </style>
  <script type="text/javascript" src="%(portalurl)s/templates/yoo_level/lib/js/mootools/mootools-release-1.12.js"></script>
  <script type="text/javascript" src="%(portalurl)s/plugins/system/mtupgrade/mootools.js"></script>
  <script type="text/javascript" src="%(portalurl)s/media/system/js/modal.js"></script>
  <script type="text/javascript" src="%(portalurl)s/modules/mod_yoo_search/mod_yoo_search.js"></script>
  <script type="text/javascript">
  // <![CDATA[
window.addEvent("domready", function() {
    SqueezeBox.initialize({});
    $$("a.modal").each(function(el) {
        el.addEvent("click", function(e) {
            new Event(e).stop();
            SqueezeBox.fromElement(el);
        });
    });
});
var YtSettings = { tplurl: '%(portalurl)s/templates/yoo_level', color: 'openaire2', itemColor: '', layout: 'left' };
// ]]>
  </script>
  <script type="text/javascript" src="%(portalurl)s/components/com_openaire/js/Meio.Autocomplete.js"></script>
  <link rel="stylesheet" href="%(portalurl)s/components/com_openaire/css/ingestion1.css" />
  <script type="text/javascript" src="%(portalurl)s/templates/yoo_level/lib/js/addons/base.js"></script>
<script type="text/javascript" src="%(portalurl)s/templates/yoo_level/lib/js/addons/accordionmenu.js"></script>
<script type="text/javascript" src="%(portalurl)s/templates/yoo_level/lib/js/addons/fancymenu.js"></script>
<script type="text/javascript" src="%(portalurl)s/templates/yoo_level/lib/js/addons/dropdownmenu.js"></script>
<script type="text/javascript" src="%(portalurl)s/templates/yoo_level/lib/js/yoo_tools.js"></script>

<link rel="apple-touch-icon" href="%(portalurl)s/templates/yoo_level/apple_touch_icon.png" />
</head>
  <body id="page" class="yoopage left   ">
    <div id="page-body">
      <div class="page-body-t">
        <div class="wrapper floatholder">
          <div id="header">
            <div id="toolbar">
              <div class="toolbar-1">
                <div class="toolbar-2">
                  <div class="mod-blank">
                    <div class="module">
                      <div class="default">
                        <div id="yoo-search-1" class="yoo-search">
                          <form action="%(portalurl)s/index.php" method="post">
                            <div class="searchbox">
                              <button class="search-magnifier" type="submit" value="Search"></button>
                              <input class="searchfield" type="text" onfocus="if(this.value=='search...') this.value='';" onblur="if(this.value=='') this.value='search...';" value="search..." size="20" alt="search..." maxlength="20" name="searchword" />
                              <button class="search-close" type="reset" value="Reset"></button>
                            </div>
                            <input type="hidden" name="task" value="search" />
                            <input type="hidden" name="option" value="com_search" />
                          </form>
                          <div class="resultbox" style="width: 400px;"></div>
                        </div>
                      </div>
                      <script type="text/javascript">
// <![[CDATA
window.addEvent('domready', function(){ new YOOsearch('yoo-search-1', { 'url': '%(site)s/deposit/portalproxy?option=com_search&tmpl=raw&type=json&ordering=&searchphrase=all&Itemid=381', 'fieldText': 'search...', 'msgResults': 'Search results', 'msgCategories': 'Search categories', 'msgNoResults': 'No results found', 'msgMoreResults': 'More results' }); });
// ]]>
</script>
                    </div>
                  </div>
                  <div class="mod-blank">
                    <div class="module">
                      <div id="jflanguageselection">
                        <ul class="jflanguageselection">
<!--<li><a href="http://www.openaire.eu/bg/how-to-deposit/orphan-repository.html" ><span lang="bg" xml:lang="bg">BG</span></a></li>-->
                          <li id="active_language">
                            <a href="javascript:;">
                              <span lang="en" xml:lang="en">EN</span>
                            </a>
                          </li>
                        </ul>
                      </div>
<!--JoomFish V2.1.3 (Twinkle)-->
<!-- &copy; 2003-2010 Think Network, released under the GPL. -->
<!-- More information: at http://www.joomfish.net -->
                    </div>
                  </div>
                  <div id="topmenu">
                    <ul class="menu">
                      <li class="level1 item10 first">
                        <a href="%(portalurl)s/en/contact-us" class="level1 item10 first">
                          <span>Contact us</span>
                        </a>
                      </li>
                      <li class="level1 item11 last">
                        <a href="%(portalurl)s/en/about-openaire/general-information/objectives" class="level1 item11 last">
                          <span>About</span>
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <div id="headerbar">
              <div class="floatbox ie_fix_floats">
                <div class="mod-rounded-header ">
                  <div class="module">
                    <div class="box-1">
                      <div class="box-2">
                        <div class="box-3 deepest">
                          <h3 class="header">
                            <span class="header-2">
                              <span class="header-3">Sign<span class="color"> In</span></span>
                            </span>
                          </h3>

                          <form action="%(portalurl)s/" method="post" name="login">
                            <span class="niftyquick" style="display: block;">
                              <span class="yoo-login">
                                <span class="logout">
                                  <span class="greeting">Hi %(username)s,</span>
                                  <span class="logout-button"><button value="Logout" name="Submit" type="submit" title="Logout">Logout</button></span>
                                  <input type="hidden" name="option" value="com_openaire" />
                                  <input type="hidden" name="view" value="logout" />
                                  <input type="hidden" name="return" value="%(return)s" />
                                </span>
                              </span>
                            </span>
                          </form>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mod-rounded-header ">
                  <div class="module">
                    <div class="box-1">
                      <div class="box-2">
                        <div class="box-3 deepest">
                          <h3 class="header">
                            <span class="header-2">
                              <span class="header-3">Follow<span class="color"> us on Twitter</span></span>
                            </span>
                          </h3>
                          <div style="text-align: center;">
                            <a href="http://www.twitter.com/OpenAIRE_eu" target="_blank">
                              <img alt="Follow OpenAIRE on Twitter" src="http://twitter-badges.s3.amazonaws.com/follow_bird-c.png" />
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div id="menubar">
              <div class="menubar-1">
                <div class="menubar-2"></div>
              </div>
            </div>
            <div id="logo" style="background-image: url('%(portalurl)s/images/stories/logo_openaire.png');background-repeat:no-repeat">
              <a href="%(portalurl)s/en/home">
                <h1 style="height: 100px; width: 300px; margin-top: 20px; font-size: 0px;">&nbsp;</h1>
              </a>
            </div>
            <div id="menu">
              <ul class="menu">
                <li class="level1 item3 first">
                  <a href="%(portalurl)s/" class="level1 item3 first">
                    <span>Home</span>
                  </a>
                </li>
                <li class="level1 item5 parent">
                  <a href="%(portalurl)s/en/open-access/open-access-overview" class="level1 item5 parent">
                    <span>Open Access in the EU</span>
                  </a>
                  <ul class="level2">
                    <li class="level2 item1 first">
                      <a href="%(portalurl)s/en/open-access/open-access-overview" class="level2 item1 first">
                        <span>Open Access Overview</span>
                      </a>
                    </li>
                    <li class="level2 item2">
                      <a href="%(portalurl)s/en/open-access/mandates-a-policies" class="level2 item2">
                        <span>Policies &amp; Mandates</span>
                      </a>
                    </li>
                    <li class="level2 item3">
                      <a href="%(portalurl)s/en/open-access/open-access-in-fp7" class="level2 item3">
                        <span>Open Access in FP7</span>
                      </a>
                    </li>
                    <li class="level2 item4 last">
                      <a href="%(portalurl)s/en/open-access/country-information" class="level2 item4 last">
                        <span>EU Member States</span>
                      </a>
                    </li>
                  </ul>
                </li>
                <li class="level1 item8 parent active">
                  <a href="%(portalurl)s/en/component/openaire/ingestion1/default/381" class="level1 item8 parent active">
                    <span>Deposit Publications</span>
                  </a>
                  <ul class="level2">
                    <li class="level2 item1 first active">
                      <a href="%(portalurl)s/en/component/openaire/ingestion1/default/381" class="level2 item1 first active">
                        <span>Deposit Publications</span>
                      </a>
                    </li>
                    <li class="level2 item2">
                      <a href="%(portalurl)s/en/component/openaire/claim1/default/563" class="level2 item2">
                        <span>Claim Publications</span>
                      </a>
                    </li>
                    <li class="level2 item3 last">
                      <a href="%(portalurl)s/en/component/openaire/claimeddocuments/default/538" class="level2 item3 last">
                        <span>
                          <span class="title">View your depositions</span>
                          <span class="sub"></span>
                        </span>
                      </a>
                    </li>
                  </ul>
                </li>
                <li class="level1 item9 parent">
                  <a href="%(portalurl)s/en/component/openaire/browse/default/390" class="level1 item9 parent">
                    <span>Search for Publications</span>
                  </a>
                  <ul class="level2">
                    <li class="level2 item1 first">
                      <a href="%(portalurl)s/en/component/openaire/browse/default/390" class="level2 item1 first">
                        <span>Search</span>
                      </a>
                    </li>
                    <li class="level2 item2">
                      <a href="%(portalurl)s/en/component/openaire/search/default/391" class="level2 item2">
                        <span>Advanced Search</span>
                      </a>
                    </li>
                    <li class="level2 item4 last">
                      <a href="%(portalurl)s/en/component/openaire/statspublications/default/539" class="level2 item4 last">
                        <span>Statistics</span>
                      </a>
                    </li>
                  </ul>
                </li>
                <li class="level1 item12 parent">
                  <a href="%(portalurl)s/en/support/faq" class="level1 item12 parent">
                    <span>Get Support</span>
                  </a>
                  <ul class="level2">
                    <li class="level2 item1 first">
                      <a href="%(portalurl)s/en/support/faq" class="level2 item1 first">
                        <span>FAQ</span>
                      </a>
                    </li>
                    <li class="level2 item2">
                      <a href="%(portalurl)s/en/support/helpdesk" class="level2 item2">
                        <span>Ask a question</span>
                      </a>
                    </li>
                    <li class="level2 item3">
                      <a href="%(portalurl)s/en/support/toolkits" class="level2 item3">
                        <span>Guides</span>
                      </a>
                    </li>
                    <li class="level2 item4">
                      <a href="%(portalurl)s/en/support/copyright" class="level2 item4">
                        <span>Copyright Issues</span>
                      </a>
                    </li>
                    <li class="level2 item5">
                      <a href="%(portalurl)s/en/support/ec-resources" class="level2 item5">
                        <span>EC Resources</span>
                      </a>
                    </li>
                    <li class="level2 item6 last">
                      <a href="%(portalurl)s/en/support/links" class="level2 item6 last">
                        <span>Related Links</span>
                      </a>
                    </li>
                  </ul>
                </li>
                <li class="level1 item14 parent">
                  <a href="%(portalurl)s/en/news-a-events/news" class="level1 item14 last parent">
                    <span>News &amp; Events</span>
                  </a>
                  <ul class="level2">
                    <li class="level2 item1 first">
                      <a href="%(portalurl)s/en/news-a-events/news" class="level2 item1 first">
                        <span>News</span>
                      </a>
                    </li>
                    <li class="level2 item2 last">
                      <a href="%(portalurl)s/en/news-a-events/events" class="level2 item2 last">
                        <span>Events</span>
                      </a>
                    </li>
                  </ul>
                </li>
                <li class="level1 item15 last parent">
                  <a href="%(portalurl)s/en/private-space.html" class="level1 item15 last parent">
                    <span>For members</span>
                  </a>
                  <ul class="level2">
                    <li class="level2 item1 first">
                      <a href="%(portalurl)s/en/private-space/project-documents.html" class="level2 item1 first">
                        <span>Project Documents</span>
                      </a>
                    </li>
                    <li class="level2 item2">
                      <a href="%(portalurl)s/en/private-space/meeting-documents.html" class="level2 item2">
                        <span>Meeting Documents</span>
                      </a>
                    </li>
                    <li class="level2 item3">
                      <a href="%(portalurl)s/en/private-space/mailing-lists.html" class="level2 item3">
                        <span>Mailing lists</span>
                      </a>
                    </li>
                    <li class="level2 item5">
                      <a href="%(portalurl)s/en/private-space/add-news.html" class="level2 item5">
                        <span>Add a News item</span>
                      </a>
                    </li>
                    <li class="level2 item6">
                      <a href="%(portalurl)s/en/private-space/add-web-link.html" class="level2 item6">
                        <span>Add a Web Link</span>
                      </a>
                    </li>
                    <li class="level2 item7">
                      <a href="%(portalurl)s/en/private-space/2010-03-11-11-34-58.html" class="level2 item7">
                        <span>Add an Event</span>
                      </a>
                    </li>
                    <li class="level2 item8">
                      <a href="%(portalurl)s/en/private-space/manage-articles.html" class="level2 item8">
                        <span>Manage Articles</span>
                      </a>
                    </li>
                    <li class="level2 item11">
                      <a href="%(portalurl)s/en/private-space/user-contact.html" class="level2 item11">
                        <span>My Contact Info</span>
                      </a>
                    </li>
                    <li class="level2 item12">
                      <a href="%(portalurl)s/en/private-space/user-data.html" class="level2 item12">
                        <span>My Personal Info</span>
                      </a>
                    </li>
                    <li class="level2 item13 last">
                      <a href="%(portalurl)s/en/private-space/helpdesk-contacts.html" class="level2 item13 last">
                        <span>HelpDesk Contacts</span>
                      </a>
                    </li>
                  </ul>
                </li>
              </ul>
            </div>
          </div>
<!-- header end -->
          <div class="shadow-l">
            <div class="shadow-r">
              <div id="middle">
                <div class="middle-b">
                  <div class="background">
                    <div id="left">
                      <div id="left_container" class="clearfix">
                        <div class="mod-window mod-menu ">
                          <div class="module">
                            <div class="box-t1">
                              <div class="box-t2">
                                <div class="box-t3"></div>
                              </div>
                            </div>
                            <div class="box-1">
                              <div class="box-2">
                                <div class="box-3 deepest">
                                  <h3 class="header">
                                    <span class="header-2">
                                      <span class="header-3">In<span class="color"> this section</span></span>
                                    </span>
                                  </h3>
                                  <ul class="menu">
                                    <li class="level1 item1 first active">
                                      <a href="%(portalurl)s/en/component/openaire/ingestion1/default/381" class="level1 item1 first active">
                                        <span>Deposit Publications</span>
                                      </a>
                                      <ul class="level2">
                                        <li class="level2 item1 first">
                                          <a href="%(portalurl)s/en/component/openaire/ingestion1/default/381" class="level2 item1 first">
                                            <span>to institutional repository</span>
                                          </a>
                                        </li>
                                        <li class="level2 item2 last active current active current">
                                          <a href="%(site)s/deposit?style=portal" class="level2 item2 last active current">
                                            <span>to orphan repository</span>
                                          </a>
                                        </li>
                                      </ul>
                                    </li>
                                    <li class="level1 item2">
                                      <a href="%(portalurl)s/en/component/openaire/claim1/default/563" class="level1 item2">
                                        <span>Claim Publications</span>
                                      </a>
                                    </li>
                                    <li class="level1 item3 last">
                                      <a href="%(portalurl)s/en/component/openaire/claimeddocuments/default/538" class="level1 item3 last">
                                        <span class="title">View your depositions</span>
                                      </a>
                                    </li>
                                  </ul>
                                </div>
                              </div>
                            </div>
                            <div class="box-b1">
                              <div class="box-b2">
                                <div class="box-b3"></div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
<!-- left end -->
                    <div id="main">
                      <div id="main_container" class="clearfix">
                        <div id="mainmiddle" class="floatbox">
                          <div id="content">
                            <div id="content_container" class="clearfix">
                              <div id="breadcrumbs">
                                <span class="breadcrumbs"><a href="%(portalurl)s/">Home</a>
                                <img src="%(portalurl)s/templates/yoo_level/images/arrow.png" alt="" />
                                <a href="%(portalurl)s/en/component/openaire/ingestion1/default/381">Deposit Publications</a>
                                <img src="%(portalurl)s/templates/yoo_level/images/arrow.png" alt="" />
                                <a href="%(portalurl)s/en/component/openaire/ingestion1/default/381">Deposit Publications</a>
                                %(crumbs)s
                                </span>
                              </div>
                              <div class="floatbox">
                                <div class="headline">
                                    <h1 class="title">%(title)s</h1>
                                </div>
                                %(body)s
                              </div>
                            </div>
                          </div>
<!-- content end -->
                        </div>
<!-- mainmiddle end -->
                      </div>
                    </div>
<!-- main end -->
                  </div>
                </div>
              </div>
<!-- middle end -->
            </div>
          </div>
          <div id="footer">
            <div class="footer-1">
              <div class="footer-2">
                <a class="anchor" href="#page"></a>
                <p style="text-align: center;"><img width="58" height="45" src="%(portalurl)s/images/stories/fp7-capacities_tr.png" alt="fp7-capacities" style="margin-top: 0px; margin-left: 0px; float: left;" /><img width="87" height="32" src="%(portalurl)s/images/stories/einfrastructure_sm.png" alt="e_infrastructures" style="margin-left: 10px; margin-top: 10px; float: left;" />Copyright &#xA9; 2010-11, OpenAIRE Consortium<br />Orphan Repository <em>Powered by</em> CERN <a href="http://invenio-software.org/" alt="Invenio" target="_blank">Invenio</a></p>
                <p style="text-align: center;">&#xA0;</p>
              </div>
            </div>
          </div>
<!-- footer end -->
        </div>
      </div>
    </div>
  <script type="text/javascript" src="/js/awstats_misc_tracker.js"></script>
  <noscript><img src="/js/awstats_misc_tracker.js?nojs=y" height=0 width=0 border=0 style="display: none"></noscript>
    <!-- Piwik -->
    <a href="http://piwik.org" title="Web analytics api" onclick="window.open(this.href);return(false);">
      <script type="text/javascript">
        // <![CDATA[
            var pkBaseURL = (("https:" == document.location.protocol) ? "https://gronik.icm.edu.pl/piwik/" : "http://gronik.icm.edu.pl/piwik/");
            document.write(unescape("%%3Cscript src='" + pkBaseURL + "piwik.js' type='text/javascript'%%3E%%3C/script%%3E"));
        // ]]>
      </script>
      <script type="text/javascript">
        // <![CDATA[
            piwik_action_name = '';
            piwik_idsite = 1;
            piwik_url = pkBaseURL + "piwik.php";
            piwik_log(piwik_action_name, piwik_idsite, piwik_url);
        // ]]>
        </script>
      <object>
        <noscript>
          <p>Web analytics api <img src="http://gronik.icm.edu.pl/piwik/piwik.php" style="border:0" alt="" /></p>
        </noscript>
      </object>
    </a>
    <!-- End Piwik Tag -->
  </body>
</html>
