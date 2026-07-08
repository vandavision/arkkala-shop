import React from 'react';
import { Helmet } from 'react-helmet-async';

const SeoMeta = ({ seoData, fallbackTitle, price, inventory, isArticle = false }) => {
    if (!seoData) return null;

    const metaTitle = seoData.og_title || seoData.title || fallbackTitle;
    const metaDesc = seoData.og_description || seoData.meta_description || '';
    
    const keywords = Array.isArray(seoData.seo_keywords) 
        ? seoData.seo_keywords.join(', ') 
        : (seoData.seo_keywords || '');
    
    const ogType = seoData.og_type || (isArticle ? 'article' : 'product');
    const ogLocale = seoData.og_locale || 'fa_IR';
    const siteName = seoData.og_site_name || 'ارک کالا';
    const robotsContent = seoData.robots || "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1";

    return (
        <Helmet>
            <title>{metaTitle} | {siteName}</title>
            {metaDesc && <meta name="description" content={metaDesc} />}
            {keywords && <meta name="keywords" content={keywords} />}
            <meta name="robots" content={robotsContent} />

            {seoData.canonical_url && <link rel="canonical" href={seoData.canonical_url} />}

            <meta property="og:title" content={metaTitle} />
            {metaDesc && <meta property="og:description" content={metaDesc} />}
            <meta property="og:type" content={ogType} />
            {(seoData.og_url || seoData.canonical_url) && <meta property="og:url" content={seoData.og_url || seoData.canonical_url} />}
            <meta property="og:site_name" content={siteName} />
            <meta property="og:locale" content={ogLocale} />
            {seoData.og_image_url && <meta property="og:image" content={seoData.og_image_url} />}

            {seoData.schema_markup && Object.keys(seoData.schema_markup).length > 0 && (
                <script type="application/ld+json">
                    {JSON.stringify(seoData.schema_markup)}
                </script>
            )}

            {!isArticle && price && (
                <>
                    <meta property="product:price:amount" content={price} />
                    <meta property="product:price:currency" content="IRT" />
                    <meta property="product:availability" content={inventory > 0 ? "instock" : "oos"} />
                </>
            )}

            {/* Article Meta */}
            {isArticle && seoData.article_author && (
                <meta property="article:author" content={seoData.article_author} />
            )}
        </Helmet>
    );
};

export default SeoMeta;