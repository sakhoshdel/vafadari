// var $ = jQuery

// // to execute on all pages
// $(document).ready(function () {

//     $('.page-buttom-desc .extend-button').click(function (){
//         $('.page-buttom-desc').toggleClass('extend-page-buttom-desc');

//         $('.page-buttom-desc .extend-button').text(function(i, text){
//             return text === "بستن" ? "مشاهده بیشتر" : "بستن";
//         })

//         $('.page-buttom-desc .extend-button').toggleClass('bi-chevron-up');
//     })
//     // to make all resize functions execute on first page run
//     onMyResize();
//     // bootstrap tooltip
//     var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
//     var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
//         return new bootstrap.Tooltip(tooltipTriggerEl)
//     })

//     // address: https://github.com/WeCodePixels/theia-sticky-sidebar
//     // $('.leftSidebar, .content, .rightSidebar').theiaStickySidebar({
//     //     additionalMarginTop: 120,
//     //     minWidth: 991.98
//     // });

//     // mobile menu search box
//     $('#mobile-search-button').click(function () {
//         $('.mobile-search').show();
//     });
//     $('.mobile-search .times').click(function () {
//         $('.mobile-search').hide();
//     });

//     // Scroll Down Detection for header-menu
//     var scrollPos = 0;
//     window.addEventListener('scroll', function () {
//         if (window.innerWidth < 991.98) {
//             if ((document.body.getBoundingClientRect()).top < scrollPos)
//                 document.getElementById('header-menu').style.top = "-60px";
//             else
//                 document.getElementById('header-menu').style.top = "0";
//             // saves the new position for iteration.
//             scrollPos = (document.body.getBoundingClientRect()).top;
//         } else {
//             if ((document.body.getBoundingClientRect()).top < scrollPos){
//                 document.getElementById('header-menu').style.top = "30px";
//                 document.getElementById('header-main').style.borderRadius = "0 0 20px 20px";
//             }
//             else {
//                 document.getElementById('header-menu').style.top = "65px";
//                 document.getElementById('header-main').style.borderRadius = "0";
//             }
//             // saves the new position for iteration.
//             scrollPos = (document.body.getBoundingClientRect()).top;
//         }
//     }, {passive: true} );

//     //menu
//     const menu = new MmenuLight(
//         document.querySelector( "#menu" )
//     );
//     const navigator = menu.navigation({
//     });
//     const drawer = menu.offcanvas({
//         position: "right"
//     });
//     document.querySelector( 'a[href="#menu"]' )
//         .addEventListener( 'click', ( evnt ) => {
//             evnt.preventDefault();
//             drawer.open();
//             document.getElementsByClassName('sidemenu-close-btn')[0].style.display = 'block';
//             document.getElementsByClassName('sidemenu-close-btn')[0].style.opacity = 1;
//         });
//     document.querySelector( 'div[class="sidemenu-close-btn"]' )
//         .addEventListener( 'click', ( evnt ) => {
//             evnt.preventDefault();
//             drawer.close();
//             //menu close line 124 in mmenu.js file
//         });
//     //live search code
//     $('.search-main input').click(function(){
//         if (!$.trim($('.search-main .search-results').html())=='')
//             $('.search-main .search-results').show();
//     })
//     // $('.search-main input').keyup(function(){
//     //     if (($('.search-main input').val().length) > 2) {
//     //         $('.search-main .search-results').show();
//     //     } else {
//     //         $('.search-main .search-results').hide();
//     //     }
//     //     if (($('.search-main input').val().length) > 2) {
//     //         $.ajax({
//     //             //passing wp-ajax url to page by wp_localize_script and reading it with this code
//     //             url: likeit.ajax_url,
//     //             type: 'post',
//     //             data: {
//     //                 action: 'prod_search',
//     //                 keyword: $('.search-main input').val(),
//     //                 nonce: $('.search-main').attr("data-nonce")
//     //             },
//     //             success: function (response) {
//     //                 $('.search-main .search-results').html(response);
//     //             }
//     //         });
//     //     }
//     // })
//     $('.search-main input').blur(function() {
//         // $('.search-main .search-results').hide();
//     })
//     //live search code-END
    
//     //make tables responsive in mobile
//     $('table').wrap('<div style="overflow-x:auto;"></div>');
    
    
//     //hide table of contents when there is nothing 
//     if ($('.table-of-contents .body-box').children().length === 0){
//         $('.table-of-contents').hide();
//     }

// })
// // to execute on all pages-END



// // put everything which needs to run on first page run (after being ready) and when page is resizing here!
// function onMyResize(){
    
//     //check if we are in home page
//     let homePageFirstRow = document.getElementById('first-row');
//     if (homePageFirstRow !=null){
//         if (window.innerWidth < 991.98) {
//             $("#forush-vije").prependTo("#first-row");
//         }else{
//             $("#forush-vije").prependTo("#sidebar-first-row");
//         }
//     }
    
//     //onresize event handler for header-menu right positioning
//     if (window.innerWidth < 991.98) {
//         document.getElementById('header-menu').style.top = "0";
//     }else{
//         document.getElementById('header-menu').style.top = "65px";
//     }
//     //onresize event handler for header-menu right positioning - END
//     // product-single page onresize calculate height of horizontal space for productDescNavbar
//     let productDescNavbar = document.getElementById('product-desc-navbar');
//     if (productDescNavbar !=null) {
//         let height = productDescNavbar.offsetHeight;
//         let horizontalSpaces = document.getElementsByClassName('horizontal-space');
//         let totalHorizontalSpaces = horizontalSpaces.length;
//         for (let i = 0; i < totalHorizontalSpaces; i++) {
//             horizontalSpaces[i].style.height = height + 'px';
//         }
//     }
//     // product-single page onresize calculate height of horizontal space for productDescNavbar - END
//     // product-single page onresize calculate height of horizontal space for stickyAddToCart
//     let stickyAddToCart = document.getElementById('sticky-add-to-cart');
//     if (stickyAddToCart !=null){
//         let StickyHeight = stickyAddToCart.offsetHeight;
//         let horizontalSpaceFooter = document.getElementsByClassName('horizontal-space-footer');
//         horizontalSpaceFooter[0].style.height = StickyHeight + 'px';
//     }
//     // product-single page onresize calculate height of horizontal space for stickyAddToCart -END
//     // product-single page onresize calculate padding of fullscreen product gallery
//     let screenHeight = window.innerHeight;
//     let screenWidth = window.innerWidth;
//     let fullscreenProductGallery = document.getElementById('product-gallery-slider-fullscreen');
//     if ( fullscreenProductGallery!= null){
//         if (screenWidth < 700){
//             if (screenHeight < 700)
//                 if (screenWidth - screenHeight > 0)
//                     fullscreenProductGallery.style.paddingTop = 0 + 'px';
//                 else
//                     fullscreenProductGallery.style.paddingTop = (screenHeight - screenWidth)/2 + 'px';
//             if (screenHeight > 700)
//                 fullscreenProductGallery.style.paddingTop = (screenHeight - screenWidth)/2 + 'px';
//         }
//         else {
//             if (screenHeight > 700)
//                 fullscreenProductGallery.style.paddingTop = (screenHeight - 700) / 2 + 'px';
//             if (screenHeight < 700)
//                 fullscreenProductGallery.style.paddingTop = 0 + 'px';
//         }
//     }
//     // product-single page onresize calculate padding of fullscreen product gallery -END
//     //shop page calculate banner widths
//     let banners = document.getElementsByClassName('wide-banner')
//     if (banners.length > 1){
//         let bannerWidth = banners[0].offsetWidth;
//         let bannerLeftTitles = document.getElementsByClassName('banner-left-title')
//         let totalLefts = bannerLeftTitles.length;
//         for ( let i = 0; i < totalLefts; i++ ) {
//             let titleWidth = bannerLeftTitles[i].offsetWidth;
//             let marginRight = ((bannerWidth/2) - titleWidth)  / 2;
//             bannerLeftTitles[i].style.marginRight = marginRight + 'px';
//         }
//         let bannerRightTitles = document.getElementsByClassName('banner-right-title')
//         let totalRights = bannerRightTitles.length;
//         for ( let i = 0; i < totalRights; i++ ) {
//             let titleWidth = bannerRightTitles[i].offsetWidth;
//             let marginRight = ((bannerWidth/2) - titleWidth)  / 2 + (bannerWidth / 2);
//             bannerRightTitles[i].style.marginRight = marginRight + 'px';
//         }
//     }
//     //shop page calculate banner widths - END

// }

// //functions to execute only on function call

// function daghProductSlider(){
//     new Swiper('.dagh-product-slider', {
//         lazy: true,
//         loop: false,
//         slidesPerView: 1,
//         slidesPerGroup: 1,
//         spaceBetween: 0,
//         loopFillGroupWithBlank: false,
//         breakpoints: {
//             400: {
//                 slidesPerGroup: 2,
//                 slidesPerView: 2
//             },
//             767.98: {
//                 slidesPerGroup: 3,
//                 slidesPerView: 3
//             },
//             1199.98: {
//                 slidesPerGroup: 4,
//                 slidesPerView: 4
//             },
//             1539.98: {
//                 slidesPerGroup: 3,
//                 slidesPerView: 6
//             }
//         },
//         pagination: {
//             el: '.swiper-pagination',
//             clickable: false,
//         },
//         navigation: {
//             nextEl: '.swiper-button-next',
//             prevEl: '.swiper-button-prev',
//         },
//     });

// }

// function blogCategorySlider(){
//     new Swiper('.blog-category-slider', {
//         lazy: true,
//         loop: true,
//         slidesPerView: 1,
//         slidesPerGroup: 1,
//         spaceBetween: 0,
//         loopFillGroupWithBlank: false,
//         breakpoints: {
//             // for example when window width is >= 400px
//             575.98: {
//                 slidesPerGroup: 1,
//                 slidesPerView: 2
//             },
//             991.98: {
//                 slidesPerGroup: 1,
//                 slidesPerView: 3
//             },
//             1399.98: {
//                 slidesPerGroup: 1,
//                 slidesPerView: 4
//             }
//         },
//         navigation: {
//             nextEl: '.swiper-button-next',
//             prevEl: '.swiper-button-prev',
//         },
//     });
// }
// function productSpecialOfferSlider(){
//     new Swiper('.product-slider-special-offer', {
//         lazy: true,
//         loop: false,
//         navigation: {
//             nextEl: '.swiper-button-next',
//             prevEl: '.swiper-button-prev',
//         },
//         autoplay: {
//             delay: 5000,
//             disableOnInteraction: true,
//         },
//     });
// }
// function productSlider(){
//      new Swiper('.product-slider', {
//         lazy: true,
//         loop: false,
//         slidesPerView: 1,
//         slidesPerGroup: 1,
//         spaceBetween: 0,
//         loopFillGroupWithBlank: false,
//         breakpoints: {
//             400: {
//                 slidesPerGroup: 2,
//                 slidesPerView: 2
//             },
//             767.98: {
//                 slidesPerGroup: 3,
//                 slidesPerView: 3
//             },
//             1199.98: {
//                 slidesPerGroup: 4,
//                 slidesPerView: 4
//             },
//             1539.98: {
//                 slidesPerGroup: 4,
//                 slidesPerView: 5
//             }
//         },
//         pagination: {
//             el: '.swiper-pagination',
//             clickable: false,
//         },
//         navigation: {
//             nextEl: '.swiper-button-next',
//             prevEl: '.swiper-button-prev',
//         },
//     });
// }
// function postSlider(){
//     new Swiper('.post-slider', {
//         lazy: true,
//         loop: false,
//         slidesPerView: 1,
//         slidesPerGroup: 1,
//         spaceBetween: 10,
//         loopFillGroupWithBlank: false,
//         breakpoints: {
//             767.98: {
//                 slidesPerGroup: 1,
//                 slidesPerView: 2
//             },
//             1199.98: {
//                 slidesPerGroup: 1,
//                 slidesPerView: 3
//             },
//             1539.98: {
//                 slidesPerGroup: 1,
//                 slidesPerView: 4
//             }
//         },
//         pagination: {
//             el: '.swiper-pagination',
//             clickable: false,
//         },
//         navigation: {
//             nextEl: '.swiper-button-next',
//             prevEl: '.swiper-button-prev',
//         },
//     });
// }

// function moshtarianProductSlider() {
//     new Swiper('.moshtarian-slider', {
//         lazy: true,
//         loop: true,
//         slidesPerView: 1,
//         slidesPerGroup: 1,
//         spaceBetween: 100,
//         loopFillGroupWithBlank: false,
//         breakpoints: {
//             991.98: {
//                 slidesPerGroup: 2,
//                 slidesPerView: 2
//             }
//         },
//         pagination: {
//             el: '.swiper-pagination',
//             clickable: false,
//         },
//         navigation: {
//             nextEl: '.swiper-button-next',
//             prevEl: '.swiper-button-prev',
//         },
//     });
// }
// function blogUsefullButton(){
//     $(document).ready(function(){
//         //blog helpful and share section
//         $('.useful-yes-button').click(function(){
//             $('.article-rate').fadeOut(500)
//             $('.share-simple').delay(500).fadeIn(500)

//             //getting needed information which is passed by the backend to the page using attrs
//             var post_id = $(this).attr('data-id'),
//                 nonce = $(this).attr("data-nonce");

//             //ajax call for like button
//             $.ajax({
//                 //passing wp-ajax url to page by wp_localize_script and reading it with this code
//                 url : likeit.ajax_url,
//                 type : 'post',
//                 data : {
//                     action : 'pt_like_it',
//                     post_id : post_id,
//                     nonce : nonce
//                 },
//                 success : function( response ) {
//                     $('.like-count').html( response );
//                 }
//             });

//         })
//         $('.useful-no-button').click(function(){
//             $('.article-rate').fadeOut(500)
//             $('.share-no').delay(500).fadeIn(500)
//         })
//     })
// }
// function threeDCoverFlowPosts(){
//     new Swiper('.swiper-3dcoverflow-posts', {
//         lazy: true,
//         loop: true,
//         effect: 'coverflow',
//         grabCursor: true,
//         spaceBetween: 10,
//         centeredSlides: true,
//         slidesPerView: 'auto',
//         coverflowEffect: {
//             rotate: 30,
//         },
//         pagination: {
//             el: '.swiper-pagination',
//         },
//         navigation: {
//             nextEl: '.swiper-button-next',
//             prevEl: '.swiper-button-prev',
//         },
//     });
// }
// function productGallerySlider(){
//     var swiper = new Swiper(".product-gallery-thumb", {
//         lazy: false,
//         loop: false,
//         spaceBetween: 5,
//         slidesPerView: 4,
//         freeMode: true,
//         watchSlidesProgress: true,
//     });
//     var swiper2 = new Swiper(".product-gallery-main", {
//         lazy: false,
//         loop: true,
//         spaceBetween: 5,
//         navigation: {
//             nextEl: ".swiper-button-next",
//             prevEl: ".swiper-button-prev",
//         },
//         thumbs: {
//             swiper: swiper,
//         },
//     });
// }
// function productGallerySliderFullScreen(){
//     $('.product-gallery-main .swiper-slide').click(function () {
//         $('#product-gallery-slider-fullscreen').show();
//         $('.product-fsg-close').show();
//         document.getElementsByTagName('body')[0].style.overflow = 'hidden';
//     });
//     window.addEventListener('keydown', function (event) {
//         if (event.key === 'Escape') {
//             $('#product-gallery-slider-fullscreen').hide();
//             $('.product-fsg-close').hide();
//             document.getElementsByTagName('body')[0].style.overflow = '';
//         }
//     })
//     $('.product-fsg-close').click(function () {
//         $('#product-gallery-slider-fullscreen').hide();
//         $('.product-fsg-close').hide();
//         document.getElementsByTagName('body')[0].style.overflow = '';
//     })
//     new Swiper("#product-gallery-slider-fullscreen", {
//         lazy: true,
//         loop: true,
//         slidesPerView: 1,
//         spaceBetween: 30,
//         keyboard: {
//             enabled: true,
//         }
//     });
// }
// function productPageScrollSpy(){
//     var link = $('#product-desc-navbar a');
//     // Run the scrNav when scroll
//     $(window).on('scroll', function(){
//         scrNav()
//         hideTopMenusOnProductPage()
//     });
//     // scrNav function
//     function scrNav() {
//         var sTop = $(window).scrollTop();
//         $('.product-contents-section section').each(function() {
//             var id = $(this).attr('id'),
//                 offset = $(this).offset().top-1,
//                 height = $(this).height();
//             if(sTop >= offset && sTop < offset + height) {
//                 link.removeClass('active-section');
//                 $('#product-desc-navbar').find('[data-scroll="' + id + '"]').addClass('active-section');
//             }
//         });
//     }
//     // product page hide and show menus when scrolling past product content section
//     function hideTopMenusOnProductPage(){
//         var scrollPos = $('#product-desc-section').offset().top;
//         window.addEventListener('scroll', function () {
//             if (window.innerWidth < 991.98) {
//                 if ((document.body.getBoundingClientRect()).top + scrollPos < 170)
//                     document.getElementById('header-menu').style.top = "-60px";
//                 else
//                     document.getElementById('header-menu').style.top = "0";
//             }else{
//                 if ((document.body.getBoundingClientRect()).top + scrollPos < 170){
//                     document.getElementById('header-main').style.top = "-75px";
//                     document.getElementById('header-menu').style.top = "-40px";
//                 }
//                 else{
//                     document.getElementById('header-main').style.top = "0";
//                     document.getElementById('header-menu').style.top = "65";
//                 }
//             }
//         }, {passive: true});
//     }
// }

// // aghsati calculator functions
// function myFunction() {
//     var price = $("#finalSelectedPrice").text().replace(/\D/g, '');
//     // console.log('price:' + price);
//     if (price === '') {
//         document.getElementById('zeroPrice').style.display = 'block';
//         return;
//     }

//     var productGheymat = price;

//     if (productGheymat == 0) {
//         document.getElementById('zeroPrice').style.display = 'block';
//         return;
//     } else if (productGheymat < 600000) {
//         document.getElementById('priceTooLow').style.display = 'block';
//         return;
//     } else {
//         document.getElementById('divCalcRes').style.display = 'block';

//         var prePaymentPercent = document.getElementById('inpPre').value;
//         var numberOfMonths = document.getElementById('inpCount').value;
//         var insDis = document.getElementById('inpInsDis').value;
//         var incPercent;
//         var baghimande;
//         var pishAmount;
//         var chequeAmount;
//         var chequeNumbers;
//         var incAmount;
//         var finalPrice;
//         var vatAmount;

//         // if (insDis == 2)
//         //     incPercent = 25;
//         // else
//         //     incPercent = 24;
        
        
//         // if (insDis == 3)
//         //     if (prePaymentPercent >= 50 && numberOfMonths <=6)
//         //         incPercent = 33;
//         //     else
//         //         incPercent = 39;
//         // else if (insDis == 2)
//         //     if (prePaymentPercent >= 50 && numberOfMonths <=6)
//         //         incPercent = 28.5;
//         //     else
//         //         incPercent = 36;
//         // else
//         //     if (prePaymentPercent >= 50 && numberOfMonths <=6)
//         //         incPercent = 24.5;
//         //     else
//         //         incPercent = 31.5;


//         if (prePaymentPercent >= 50)
//             incPercent = 1.8;
//         else
//             incPercent = 2.25;

        
//         //   if (insDis == 3)
//         //         incPercent = 36.2;
//         // else if (insDis == 2)
//         //         incPercent = 31.5;
//         // else
//         //         incPercent = 27;



//         //BUSINESS
//         pishAmount = (productGheymat * prePaymentPercent) / 100;
//         baghimande = productGheymat - pishAmount;

//         if (insDis == 3) {
//             chequeNumbers = Math.floor(Number(numberOfMonths) / 3);
//             let ghest = calcGhest(baghimande, incPercent, chequeNumbers, 3);
//             chequeAmount = ghest;
//             chequeAmount = Math.round(chequeAmount / 1000) * 1000;
//         }
//         else if (insDis == 2) {
//             chequeNumbers = Math.floor(Number(numberOfMonths) / 2);
//             let ghest = calcGhest(baghimande, incPercent, chequeNumbers, 2);
//             chequeAmount = ghest;
//             chequeAmount = Math.round(chequeAmount / 1000) * 1000;
//         } else {
//             chequeNumbers = Number(numberOfMonths);
//             let ghest = calcGhest(baghimande, incPercent, chequeNumbers, 1);
//             chequeAmount = Math.round(ghest / 1000) * 1000;
//         }

//         incAmount = (chequeNumbers * chequeAmount) + pishAmount - productGheymat;
  
//         let incMonthAmount = incAmount / numberOfMonths;
//         vatAmount = Math.round((incAmount * 9) / 100);
//         finalPrice = (chequeAmount * chequeNumbers) + pishAmount + vatAmount;

//         // if (chequeAmount > 800000)
//         //     document.getElementById('chequetoohigh').style.display = 'block';

//         if (chequeAmount > 4500000)
//             document.getElementById('chequetoohigh').style.display = 'block';
//         else if (chequeAmount > 2000000)
//             document.getElementById('chequelimitzone').style.display = 'block';

//         document.getElementById('finalAmount').textContent = addCommas(Math.round(productGheymat));
//         document.getElementById('pishAmount').textContent = addCommas(Math.round(pishAmount));
//         document.getElementById('remainingAmount').textContent = addCommas(Math.round(baghimande));
//         document.getElementById('chequeAmount').textContent = addCommas(Math.round(chequeAmount));
//         document.getElementById('chequeNumbers').textContent = addCommas(Math.round(chequeNumbers));
//         document.getElementById('incMonthAmount').textContent = addCommas(Math.round(incMonthAmount));
//         document.getElementById('incAmount').textContent = addCommas(Math.round(incAmount));
//         document.getElementById('vatAmount').textContent = addCommas(Math.round(vatAmount));
//         document.getElementById('finalPrice').textContent = addCommas(Math.round(finalPrice));
//     }
// }
// function calcGhest(baghimande, nerkhMahniyane, checkNumbers, harchandmah) {
//     let nerkhDarsad = nerkhMahniyane *2;
//     let aghsat = baghimande / (checkNumbers * (1 - ((1 + checkNumbers) * harchandmah * (nerkhDarsad/100)) / 2));
//     return Math.round( aghsat );
// }
// function addCommas(nStr) {
//     nStr += '';
//     x = nStr.split('.');
//     x1 = x[0];
//     x2 = x.length > 1 ? '.' + x[1] : '';
//     var rgx = /(\d+)(\d{3})/;
//     while (rgx.test(x1)) {
//         x1 = x1.replace(rgx, '$1' + '٫' + '$2');
//     }
//     return x1 + x2;
// }
// function hideCalc() {
//     document.getElementById('divCalcRes').style.display = 'none';
//     document.getElementById('chequetoohigh').style.display = 'none';
//     document.getElementById('chequelimitzone').style.display = 'none';
//     document.getElementById('noOptions').style.display = 'none';
//     document.getElementById('zeroPrice').style.display = 'none';
// }
// // aghsati calculator functions- END
// function productPageAdditionalJSCode(){

//     document.addEventListener(
//         "DOMContentLoaded", () => {
            
//             //   //show stars on product page. todo: later maybe rate my post plugin used instead
//             // $("#rating").hide().before('<p class="stars">\t\t\t\t\t\t<span>\t\t\t\t\t\t\t<a class="star-1" href="#">1</a>\t\t\t\t\t\t\t<a class="star-2" href="#">2</a>\t\t\t\t\t\t\t<a class="star-3" href="#">3</a>\t\t\t\t\t\t\t<a class="star-4" href="#">4</a>\t\t\t\t\t\t\t<a class="star-5" href="#">5</a>\t\t\t\t\t\t</span>\t\t\t\t\t</p>')
//             // $('#respond p.stars a').click(function() {
//             //     var t = $(this)
//             //         , e = $(this).closest("#respond").find("#rating")
//             //         , i = $(this).closest(".stars");
//             //     return e.val(t.text()),
//             //         t.siblings("a").removeClass("active"),
//             //         t.addClass("active"),
//             //         i.addClass("selected"),
//             //         !1
//             // });
//             // $('#respond #submit').click(function() {
//             //     var t = $(this).closest("#respond").find("#rating")
//             //         , e = t.val();
//             //     if (0 < t.length && !e && "yes" === wc_single_product_params.review_rating_required)
//             //         return window.alert(wc_single_product_params.i18n_required_rating_text),
//             //             !1
//             // });
            
//               //set no aghsati for vars on page load
//             let aghsati = $('.variation-active').attr("aghsati");
//             if (aghsati == 'no'){
//                 $('#aghsatiModal .no-aghsati').show();
//                 $('#aghsatiModal .yes-aghsati').hide();
//             }else{
//                 $('#aghsatiModal .no-aghsati').hide();
//                 $('#aghsatiModal .yes-aghsati').show();
//             }
            
//             // fixing header menus animation when modals open
//             let myAghsatiModal = document.getElementById('aghsatiModal')
//             myAghsatiModal.addEventListener('show.bs.modal', function (event) {
//                 $('header > div').toggleClass('aghsati-modal-fix')
//             })
//             myAghsatiModal.addEventListener('hidden.bs.modal', function (event) {
//                 $('header > div').toggleClass('aghsati-modal-fix')
//             })
//             let shareModal = document.getElementById('shareModal')
//             shareModal.addEventListener('show.bs.modal', function (event) {
//                 $('header > div').toggleClass('aghsati-modal-fix')
//             })
//             shareModal.addEventListener('hidden.bs.modal', function (event) {
//                 $('header > div').toggleClass('aghsati-modal-fix')
//             })
            
//             //takhfif message on first run
//             let pricehtml = $('.variation-active div div ins span bdi').html();
//             //if sale price exists and is active on first run then...
//             if (pricehtml != null) {

//                 let oldPricehtml = $('.variation-active div div span bdi').html()

//                 //takhfif message show
//                 let myOldPricehtml = oldPricehtml.replaceAll(/\D/g, '');
//                 let myPricehtml = pricehtml.replaceAll(/\D/g, '');

//                 let priceDef = myOldPricehtml - myPricehtml;
//                 $('.priceDef').html(addCommas(priceDef));
//                 $('.takhfif-message').css("display", "block");
//             }

//             // product variables selection
//             $('.product-var').each(function(){
//                 $(this).click(function(){
//                     // var selection style
//                     $(this).parent().children().removeClass('variation-active');
//                     $(this).addClass('variation-active');

//                     //price change to everywhere
//                     //first sale price
//                     let pricehtml = $('.variation-active div div ins span bdi').html();
//                     //if no sale price then normal price
//                     if (pricehtml == null){
//                         //takhfif message hide
//                         $('.takhfif-message').hide()
//                         pricehtml = $('.variation-active div div span bdi').html()
//                     }else {

//                         let oldPricehtml = $('.variation-active div div span bdi').html()

//                         //takhfif message show
//                         let myOldPricehtml = oldPricehtml.replaceAll(/\D/g,'');
//                         let myPricehtml = pricehtml.replaceAll(/\D/g,'');

//                         let priceDef = myOldPricehtml - myPricehtml;
//                         $('.priceDef').html(addCommas(priceDef));
//                         $('.takhfif-message').css("display", "block");

//                     }
                    
//                     $('#finalSelectedPrice span bdi').html(pricehtml);
//                     $('.buttom-product-info-box span bdi').html(pricehtml);
//                     $('#sticky-add-to-cart span bdi').html(pricehtml);

//                     // guarranty change to left product info box
//                     let guarrantyy = $('.variation-active .pa_guarantee').html();
//                         $('.left-product-info-box .guarranty').html(guarrantyy);

//                     // attrs change to buttom and sticky section
//                     let attrs = $('.variation-active .variation-name').html();
//                     $('#sticky-add-to-cart .variation-name').html(attrs);
//                     $('.buttom-product-info-box .variation-name').html(attrs);

//                     //img to buttom section
//                     let img = $('.variation-active img').clone();
//                     $('.buttom-product-info-box img').replaceWith(img);

//                     // change url of add to cart btns
//                     let addToCartUrl = $(this).attr("add-to-cart-url");
//                     $('.left-product-info-box .add-cart-btn ').attr("href", addToCartUrl);
//                     $('.buttom-product-info-box .add-cart-btn').attr("href", addToCartUrl);
//                     $('#sticky-add-to-cart .add-cart-btn').attr("href", addToCartUrl);

//                     //change delivery type in 3 places: left box, left bottom box, mobile delivery modal box
//                     let deliveryType = $(this).attr("delivery_type");
//                     var tabriz_text, tabriz_hover, others_text, others_hover  = null;
//                     if ( deliveryType == 'فوری' ) {
//                         tabriz_text  = 'تحویل فوری';
//                         tabriz_hover = 'تحویل فوری در فروشگاه حضوری و ارسال فوری برای داخل شهر تبریز (بجز روزهای تعطیل رسمی).';
//                         others_text  = 'ارسال فوری';
//                         others_hover = 'خرید تا ساعت ۱۳ روز کاری، ارسال امروز و خریدهای بعد از آن فردا صبح به مقصد مورد نظر ارسال می‌گردد.';
//                     } else if ( deliveryType == 'یکروزه' ) {
//                         tabriz_text  = 'تحویل یک روزه';
//                         tabriz_hover = 'تحویل روز کاری بعدی در فروشگاه حضوری و ارسال روز کاری بعدی برای داخل شهر تبریز.';
//                         others_text  = 'ارسال یک روزه';
//                         others_hover = 'مرسوله در روز کاری بعدی به مقصد شهر مورد نظر ارسال می‌گردد.';
//                     } else if ( deliveryType == 'دوروزه' ) {
//                         tabriz_text  = 'تحویل دو روزه';
//                         tabriz_hover = 'تحویل حداکثر ۲ روز کاری بعدی در فروشگاه حضوری و ارسال حداکثر ۲ روز کاری بعدی برای داخل شهر تبریز.';
//                         others_text  = 'ارسال دو روزه';
//                         others_hover = 'مرسوله حداکثر ۲ روز کاری بعد از ثبت سفارش به مقصد شهر مورد نظر ارسال می‌گردد.';
//                     } else if ( deliveryType == 'چهارروزه' ) {
//                         tabriz_text  = 'تحویل چهار روزه';
//                         tabriz_hover = 'تحویل حداکثر ۴ روز کاری بعدی در فروشگاه حضوری و ارسال حداکثر ۴ روز کاری بعدی برای داخل شهر تبریز.';
//                         others_text  = 'ارسال چهار روزه';
//                         others_hover = 'مرسوله حداکثر ۴ روز کاری بعد از ثبت سفارش به مقصد شهر مورد نظر ارسال می‌گردد.';
//                     } else {
//                         //default to یکساعته
//                         tabriz_text  = 'تحویل یک ساعته';
//                         tabriz_hover = 'تحویل یک ساعته در فروشگاه حضوری و ارسال یک ساعته برای داخل شهر تبریز (بجز روزهای تعطیل رسمی).';
//                         others_text  = 'ارسال فوری';
//                         others_hover = 'خرید تا ساعت ۱۳ روز کاری، ارسال امروز و خریدهای بعد از آن صبح روز کاری بعدی به مقصد مورد نظر ارسال می‌گردد.';
//                     }
//                     //left box
//                     $('.left-product-info-box .tabriz ').html(tabriz_text);
//                     $('.left-product-info-box .tabriz ').attr("data-bs-original-title", tabriz_hover);
//                     $('.left-product-info-box .others b').html(others_text);
//                     $('.left-product-info-box .others ').attr("data-bs-original-title", others_hover);

//                     //buttom box
//                     $('.buttom-product-info-box .tabriz ').html(tabriz_text);
//                     $('.buttom-product-info-box .tabriz ').attr("data-bs-original-title", tabriz_hover);
//                     $('.buttom-product-info-box .others ').html(others_text);
//                     $('.buttom-product-info-box .others ').attr("data-bs-original-title", others_hover);

//                     //mobile delivery modal box
//                     $('#ersalModal .tabriz ').html(tabriz_text);
//                     $('#ersalModal .tabriz ').attr("data-bs-original-title", tabriz_hover);
//                     $('#ersalModal .others ').html(others_text);
//                     $('#ersalModal .others ').attr("data-bs-original-title", others_hover);
                    
//                     //set full image to gallery
//                     let imageURL = $(this).attr("full-image-url");
//                     let IMG = document.createElement('img');
//                     IMG.src = imageURL
//                     $('.product-gallery-main .swiper-slide-active').html(IMG);
                    
//                   //set no aghsati for vars on click
//                     let aghsati = $(this).attr("aghsati");
//                     if (aghsati == 'no'){
//                         $('#aghsatiModal .no-aghsati').show();
//                         $('#aghsatiModal .yes-aghsati').hide();
//                     }else{
//                         $('#aghsatiModal .no-aghsati').hide();
//                         $('#aghsatiModal .yes-aghsati').show();
//                     }
                    
//                 });
//             });
//         }
//     )
// }
// //redirection with query string helper function for product tax page
// // not used anywhere yet! todo: delete if not needed later
// function updateQueryStringParameterAndRedirect(uri, key, value) {
//     let final = ''
//     var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
//     var separator = uri.indexOf('?') !== -1 ? "&" : "?";
//     if (uri.match(re)) {
//         final = uri.replace(re, '$1' + key + "=" + value + '$2');
//     }
//     else {
//         final = uri + separator + key + "=" + value;
//     }
//     window.location.href = final
// }

// //functions to execute only on function call-END

$(document).ready(function(){
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

})