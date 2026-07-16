import React from 'react';
import { Helmet } from 'react-helmet-async';

const SeoMeta = ({ seoData, fallbackTitle, price, inventory, isArticle = false, customImage, customSchema, slug }) => {
    if (!seoData) return null;

    const currentUrl = typeof window !== 'undefined' ? window.location.href.split('?')[0] : '';
    const currentOrigin = typeof window !== 'undefined' ? window.location.origin : 'https://arkkala.com';
    const baseUrl = import.meta.env.VITE_API_BASE_URL 
        ? import.meta.env.VITE_API_BASE_URL.replace(/\/api\/?$/, '').replace(/\/$/, '') 
        : currentOrigin;

    const metaTitle = seoData.og_title || seoData.title || fallbackTitle;
    let metaDesc = seoData.og_description || seoData.meta_description || seoData.short_description || seoData.description || '';
    const siteName = seoData.og_site_name || 'ارک کالا';

    if (metaDesc && metaDesc.length > 0 && metaDesc.length < 120) {
        metaDesc = `${metaDesc} | نقد و بررسی تخصصی، انتخاب هوشمندانه و خرید آنلاین با تضمین بهترین قیمت و اصالت کالا در فروشگاه اینترنتی ${siteName}.`;
    }
    if (metaDesc.length > 157) metaDesc = metaDesc.substring(0, 157) + '...';
    
    const keywords = Array.isArray(seoData.seo_keywords) ? seoData.seo_keywords.join(', ') : (seoData.seo_keywords || '');
    const ogType = seoData.og_type || (isArticle ? 'article' : 'product');
    const ogLocale = seoData.og_locale || 'fa_IR';
    const robotsContent = seoData.robots || "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1";
    const canonicalUrl = currentUrl || (seoData.canonical_url || `${baseUrl}/`);
    
    let imageUrl = customImage || seoData.og_image_url || seoData.image || seoData.image_url || '/assets/image/logo.png';
    if (imageUrl && imageUrl.startsWith('/')) imageUrl = `${baseUrl}${imageUrl}`;
    
    const twitterCard = seoData.twitter_card || 'summary_large_image';
    const twitterSite = seoData.twitter_site || '@arkkala';
    const twitterCreator = seoData.twitter_creator || '';

    const finalSchema = customSchema || seoData.schema_markup || seoData.json_ld;
    
    const orgSchema = {
        "@type": "Organization",
        "name": siteName,
        "url": baseUrl,
        "logo": `${baseUrl}/assets/image/logo.png`
    };
    
    const websiteSchema = {
        "@type": "WebSite",
        "name": siteName,
        "url": baseUrl,
        "potentialAction": {
            "@type": "SearchAction",
            "target": `${baseUrl}/shop?search={search_term_string}`,
            "query-input": "required name=search_term_string"
        }
    };

    let parsedSchema = finalSchema;
    if (typeof finalSchema === 'string') {
        try {
            parsedSchema = JSON.parse(finalSchema);
        } catch (e) {
            console.error("Invalid JSON-LD string:", e);
            parsedSchema = null;
        }
    }

    let schemaGraph = [orgSchema, websiteSchema];
    if (parsedSchema && typeof parsedSchema === 'object') {
        if (parsedSchema['@graph']) {
            schemaGraph = [...schemaGraph, ...parsedSchema['@graph']];
        } else {
            const { '@context': _, ...restSchema } = parsedSchema;
            schemaGraph.push(restSchema);
        }
    }

    const compiledSchema = { "@context": "https://schema.org", "@graph": schemaGraph };
    const modifiedAt = seoData.modified_at || new Date().toISOString();

    return (
        <Helmet>
            <html lang="fa" dir="rtl" />
            <title>{metaTitle} | {siteName}</title>
            {metaDesc && <meta name="description" content={metaDesc} />}
            {keywords && <meta name="keywords" content={keywords} />}
            <meta name="robots" content={robotsContent} />
            <meta name="theme-color" content="#ef4056" />

            <link rel="preconnect" href={baseUrl} crossorigin="use-credentials" />
            <link rel="dns-prefetch" href={baseUrl} />
            {imageUrl && <link rel="preload" as="image" href={imageUrl} fetchpriority="high" />}

            {canonicalUrl && <link rel="canonical" href={canonicalUrl} />}

            <meta property="og:title" content={metaTitle} />
            {metaDesc && <meta property="og:description" content={metaDesc} />}
            <meta property="og:type" content={ogType} />
            {canonicalUrl && <meta property="og:url" content={canonicalUrl} />}
            <meta property="og:site_name" content={siteName} />
            <meta property="og:locale" content={ogLocale} />
            {imageUrl && <meta property="og:image" content={imageUrl} />}
            <meta property="og:updated_time" content={modifiedAt} />

            <meta name="twitter:card" content={twitterCard} />
            <meta name="twitter:title" content={metaTitle} />
            {metaDesc && <meta name="twitter:description" content={metaDesc} />}
            {imageUrl && <meta name="twitter:image" content={imageUrl} />}
            {twitterSite && <meta name="twitter:site" content={twitterSite} />}
            {twitterCreator && <meta name="twitter:creator" content={twitterCreator} />}

            <script type="application/ld+json">
                {JSON.stringify(compiledSchema)}
            </script>

            {!isArticle && price && <meta property="product:price:amount" content={price.toString()} />}
            {!isArticle && price && <meta property="product:price:currency" content="IRT" />}
            {!isArticle && inventory !== undefined && <meta property="product:availability" content={inventory > 0 ? "instock" : "oos"} />}
            {isArticle && seoData.article_author && <meta property="article:author" content={seoData.article_author} />}
            {isArticle && <meta property="article:modified_time" content={modifiedAt} />}
        </Helmet>
    );
};

export default SeoMeta;