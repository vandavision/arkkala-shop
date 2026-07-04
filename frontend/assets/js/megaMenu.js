$(document).ready(function () {

    // Toggle submenu when a '.showSubMenu' element is clicked
    $(".showSubMenu").click(function () {
        $(this).nextAll("ul").toggleClass("show"); // Toggle 'show' class on the next 'ul' elements
        $(this).toggleClass('open'); // Toggle 'open' class on the clicked element
    });

    let mainMenuHead = jQuery('.main-menu-head');

    // Show submenu when hovering over '.main-menu-head'
    $(mainMenuHead).hover(function () {
        $(this).children().find(".main-menu-sub").first().addClass('main-menu-sub-active'); // Add active class to submenu
        $(this).children().addClass('active'); // Mark the parent as active
    });

    // Hide submenu when mouse leaves '.main-menu-head'
    $(mainMenuHead).mouseleave(function () {
        $(this).children().find(".main-menu-sub").first().removeClass('main-menu-sub-active'); // Remove active class from submenu
        $(this).children().removeClass('active'); // Remove active class from parent
    });

    // Handle submenu activation when hovering over '.main-menu li'
    $(".main-menu li").mouseover(function () {
        $(".main-menu li").removeClass("main-menu-sub-active-li"); // Remove active class from all menu items
        $(this).addClass("main-menu-sub-active-li"); // Add active class to hovered item
        $(".main-menu-sub").removeClass('main-menu-sub-active'); // Remove active class from all submenus
        $(this).children('ul').removeClass('main-menu-sub-active'); // Reset submenu state
        $(this).children('ul').addClass('main-menu-sub-active'); // Activate submenu for the hovered item
    });

    // Remove active class when mouse leaves the active submenu
    $(".main-menu-sub-active").mouseleave(function () {
        $(".main-menu-sub-active").removeClass("main-menu-sub-active");
    });

});

/**
 * Sticky Mega Menu - Makes the mega menu hide when scrolling down and reappear when scrolling up
 */
document.addEventListener("DOMContentLoaded", function () {
    let lastScrollTop = 0; // Track the last scroll position
    const delta = 50; // Minimum scroll difference before triggering menu changes
    const megaMenu = document.querySelector(".mega-menu"); // Select mega menu
    const header = document.querySelector(".header"); // Select header

    if (!megaMenu || !header) return; // Ensure elements exist before proceeding

    window.addEventListener("scroll", function () {
        let nowScrollTop = window.scrollY || document.documentElement.scrollTop;

        // Only trigger if scroll difference is significant
        if (Math.abs(lastScrollTop - nowScrollTop) < delta) {
            return;
        }

        if (nowScrollTop > lastScrollTop) {
            // Scrolling down: Hide mega menu and add shadow to header
            megaMenu.classList.remove("mega-menu-top");
            header.classList.add("shadow-md", "pb-3");
        } else {
            // Scrolling up: Show mega menu and remove shadow from header
            megaMenu.classList.add("mega-menu-top");
            header.classList.remove("shadow-md", "pb-3");
        }

        lastScrollTop = nowScrollTop; // Update last scroll position
    });
});




/* ----------------------------------------
   New Mega Menu – Vanilla JavaScript (with hover close)
----------------------------------------- */
document.addEventListener('DOMContentLoaded', function () {
    const menuItems = document.querySelectorAll('.custom-mega-category');
    const panels = document.querySelectorAll('.custom-mega-panel');
    const megaMenu = document.querySelector('.custom-mega-menu');
    const megaContent = document.querySelector('.custom-mega-content');
    const megaTrigger = document.querySelector('.custom-mega-trigger');

    // Set default active panel
    const defaultPanel = document.querySelector('[data-mega-target="4"]');
    if (defaultPanel) {
        defaultPanel.classList.add('active');
    }

    // Switch panel on hover
    menuItems.forEach(item => {
        item.addEventListener('mouseenter', function () {
            const targetId = this.getAttribute('data-mega-id');

            // Deactivate all items
            menuItems.forEach(i => i.classList.remove('active'));

            // Activate current item
            this.classList.add('active');

            // Hide all panels
            panels.forEach(panel => panel.classList.remove('active'));

            // Show related panel
            const targetPanel = document.querySelector(`[data-mega-target="${targetId}"]`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });

    // Close mega menu when mouse leaves the menu area
    if (megaMenu && megaContent) {
        megaMenu.addEventListener('mouseleave', function () {
            megaContent.style.display = 'none';
        });

        // Optional: re-open when hovered again
        megaMenu.addEventListener('mouseenter', function () {
            megaContent.style.display = 'block';
        });
    }

    // Show mega menu when hovering over the trigger
    if (megaTrigger && megaContent) {
        megaTrigger.addEventListener('mouseenter', function () {
            megaContent.style.display = 'block';
        });
    }
});
