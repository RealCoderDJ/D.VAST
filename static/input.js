
        var coll = document.getElementsByClassName("collapsible");
        var i;

        for (i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.maxHeight){
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
            });
        }

        function yesnoCheck() {
            if (document.getElementById('yesCheck').checked) {
                document.getElementById('ifYes').style.visibility = 'visible';
            }
            else document.getElementById('ifYes').style.visibility = 'hidden';
        }


       function overlaying(){
            var x = document.getElementsByClassName("overlay");
            var i;
            for (i = 0; i < x.length; i++) {
                x[i].style.display = 'block';
            }
            var y = document.getElementsByClassName("overlay_text");
            for (i = 0; i < y.length; i++) {
                y[i].style.display = 'block';
            }
            var z = document.getElementsByClassName("loading");
            var i;
            for (i = 0; i < z.length; i++) {
                z[i].style.display = 'block';
            }
        }

        function refreshoverlaying() {
            var x = document.getElementsByClassName("overlay");
            var i;
            for (i = 0; i < x.length; i++) {
                x[i].style.display = 'none';
            }
            var y = document.getElementsByClassName("overlay_text");
            for (i = 0; i < y.length; i++) {
                y[i].style.display = 'none';
            }
            var z = document.getElementsByClassName("loading");
            var i;
            for (i = 0; i < z.length; i++) {
                z[i].style.display = 'none';
            }
        }


/*        var preloader=document.getElementById('loading');
        var preloader2=document.getElementById('loading2');
        var preloader3=document.getElementById('loading3');
        var preloader4=document.getElementById('loading4');
        function myLoadingFunction() {
            preloader.style.display="block";
        }
        function myLoadingFunction2() {
            preloader2.style.display="block";
        }
        function myLoadingFunction3() {
            preloader3.style.display="block";
        }
        function myLoadingFunction4() {
            preloader4.style.display="block";
        }
        function myFunction(){
            preloader4.style.display='none';
            preloader3.style.display='none';
            preloader2.style.display='none';
            preloader.style.display='none';
        }
*/