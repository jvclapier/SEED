//login screen animation
var container_intro = document.getElementById('intro-animation');
 // Set up our animation

 var animData_intro = {
     container: container_intro,
     renderer: 'svg',
     autoplay: true,
     loop: false,
     path : path_intro
 };
 var anim_intro = bodymovin.loadAnimation(animData_intro);

 // document.getElementById('logout').addEventListener('mouseover', function(){ anim_logout.play(); });
 //
 // document.getElementById('logout').addEventListener('mouseout', function(){ anim_logout.stop(); });
