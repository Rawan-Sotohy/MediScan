// Load List 
const ul = document.querySelector( "header .content .nav ul" );
const icon = document.querySelector( "header .content .nav .click" );
icon.addEventListener( "click", () =>
{
        ul.classList.toggle( "hide" );
} );

//Lazy Load 
const lazySection = document.querySelectorAll( ".lazy-section" );
const sectionObserver = new IntersectionObserver( ( entries ) =>
{
        entries.forEach( entry =>
        {
                if ( entry.isIntersecting )
                {
                        entry.target.classList.add( "visiable" );
                        sectionObserver.unobserve( entry.target );
                }
        } );
} );
lazySection.forEach( section => sectionObserver.observe( section ) );

//Get Full Year 
document.querySelector( "footer .year" ).innerHTML = new Date().getFullYear();