import React from 'react';
import { Helmet } from 'react-helmet-async';

const SeoMeta = ({ seoData, fallbackTitle, price, inventory, isArticle = false }) => {
    if (!seoData) return null;

    const baseUrl = import.meta.env.VITE_API_BASE_URL 
        ? import.meta.env.VITE_API_BASE_URL.replace(/\/api\/?$/, '').replace(/\/$/, '') 
        : window.location.origin;

    const metaTitle = seoData.og_title || seoData.title || fallbackTitle;
    const metaDesc = seoData.og_description || seoData.meta_description || seoData.short_description || seoData.description || '';
    
    const keywords = Array.isArray(seoData.seo_keywords) 
        ? seoData.seo_keywords.join(', ') 
        : (seoData.seo_keywords || '');
    
    const ogType = seoData.og_type || (isArticle ? 'article' : 'product');
    const ogLocale = seoData.og_locale || 'fa_IR';
    const siteName = seoData.og_site_name || 'ارک کالا';
    const robotsContent = seoData.robots || "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1";
    
    const canonicalUrl = seoData.canonical_url || (typeof window !== 'undefined' ? window.location.href.split('?')[0] : '');
    
    let imageUrl = seoData.og_image_url || seoData.image || seoData.image_url || '/assets/image/site/logo.png';
    if (imageUrl && imageUrl.startsWith('/')) {
        imageUrl = `${baseUrl}${imageUrl}`;
    }
    
    const twitterCard = seoData.twitter_card || 'summary_large_image';
    const twitterSite = seoData.twitter_site || '@arkkala';
    const twitterCreator = seoData.twitter_creator || '';

    return (
        <Helmet htmlAttributes={{ lang: 'fa', dir: 'rtl' }}>
            <title>{metaTitle} | {siteName}</title>
            {metaDesc && <meta name="description" content={metaDesc} />}
            {keywords && <meta name="keywords" content={keywords} />}
            <meta name="robots" content={robotsContent} />
            <meta name="theme-color" content="#ef4056" />

            {canonicalUrl && <link rel="canonical" href={canonicalUrl} />}

            <meta property="og:title" content={metaTitle} />
            {metaDesc && <meta property="og:description" content={metaDesc} />}
            <meta property="og:type" content={ogType} />
            {canonicalUrl && <meta property="og:url" content={canonicalUrl} />}
            <meta property="og:site_name" content={siteName} />
            <meta property="og:locale" content={ogLocale} />
            {imageUrl && <meta property="og:image" content={imageUrl} />}

            <meta name="twitter:card" content={twitterCard} />
            <meta name="twitter:title" content={metaTitle} />
            {metaDesc && <meta name="twitter:description" content={metaDesc} />}
            {imageUrl && <meta name="twitter:image" content={imageUrl} />}
            {twitterSite && <meta name="twitter:site" content={twitterSite} />}
            {twitterCreator && <meta name="twitter:creator" content={twitterCreator} />}

            {seoData.schema_markup && Object.keys(seoData.schema_markup).length > 0 && (
                <script type="application/ld+json">
                    {JSON.stringify(seoData.schema_markup)}
                </script>
            )}

            {!isArticle && price && (
                <>
                    <meta property="product:price:amount" content={price} />
                    <meta property="product:price:currency" content="IRT" />
                </>
            )}
            {!isArticle && inventory !== undefined && (
                <meta property="product:availability" content={inventory > 0 ? "instock" : "oos"} />
            )}

            {isArticle && seoData.article_author && (
                <meta property="article:author" content={seoData.article_author} />
            )}
        </Helmet>
    );
};

export default SeoMeta;