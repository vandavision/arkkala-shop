import React from 'react';
import { Helmet } from 'react-helmet-async';

const SeoMeta = ({ seoData, fallbackTitle, price, oldPrice, inventory, isArticle = false, customImage, customSchema, slug, productId, guarantee, brand }) => {
    if (!seoData) return null;

    const baseUrl = import.meta.env.VITE_FRONTEND_URL || 'https://arkkala.com';
    const cleanBaseUrl = baseUrl.replace(/\/$/, '');

    const metaTitle = seoData.og_title || seoData.title || fallbackTitle || 'محصول بدون نام';
    const siteName = seoData.og_site_name || 'ارک کالا';
    const fullTitle = metaTitle.includes(siteName) ? metaTitle : `${metaTitle} | ${siteName}`;

    let metaDesc = seoData.og_description || seoData.meta_description || seoData.short_description || seoData.description || '';

    if (!metaDesc || metaDesc.trim() === '') {
        metaDesc = `خرید و قیمت ${metaTitle} در فروشگاه اینترنتی ${siteName}. بررسی مشخصات و خرید آنلاین با تضمین بهترین قیمت.`;
    } else if (metaDesc.length < 120) {
        metaDesc = `${metaDesc} | نقد و بررسی تخصصی، انتخاب هوشمندانه و خرید آنلاین با تضمین بهترین قیمت و اصالت کالا در فروشگاه اینترنتی ${siteName}.`;
    }

    if (metaDesc.length > 157) {
        metaDesc = metaDesc.substring(0, 154) + '...';
    }

    const keywords = Array.isArray(seoData.seo_keywords) ? seoData.seo_keywords.join(', ') : (seoData.seo_keywords || '');
    const ogType = seoData.og_type || (isArticle ? 'article' : 'product');
    const ogLocale = seoData.og_locale || 'fa_IR';
    const robotsContent = seoData.robots || "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1";

    // داینامیک کردن قطعی تگ Canonical (حل ارور Self-Referencing در تست سئو)
    let canonicalUrl = '';
    if (typeof window !== 'undefined') {
        canonicalUrl = window.location.origin + window.location.pathname;
    } else {
        if (seoData.canonical_url) {
            canonicalUrl = seoData.canonical_url.replace(/http:\/\/(localhost|nginx|127\.0\.0\.1)(:\d+)?/g, cleanBaseUrl);
        } else {
            canonicalUrl = `${cleanBaseUrl}${isArticle ? '/blog/' : '/product/'}${slug || ''}`;
        }
    }

    let imageUrl = customImage || seoData.og_image_url || seoData.image || seoData.image_url || '/assets/image/logo.png';
    if (imageUrl && imageUrl.startsWith('/')) {
        imageUrl = `${cleanBaseUrl}${imageUrl}`;
    }
    imageUrl = imageUrl.replace(/http:\/\/(localhost|nginx|127\.0\.0\.1)(:\d+)?/g, cleanBaseUrl);

    const twitterCard = seoData.twitter_card || 'summary_large_image';
    const twitterSite = seoData.twitter_site || '@arkkala';
    const twitterCreator = seoData.twitter_creator || '';

    const finalSchema = customSchema || seoData.schema_markup || seoData.json_ld;

    const orgSchema = {
        "@type": "Organization",
        "name": siteName,
        "url": cleanBaseUrl,
        "logo": `${cleanBaseUrl}/assets/image/logo.png`
    };

    const websiteSchema = {
        "@type": "WebSite",
        "name": siteName,
        "url": cleanBaseUrl,
        "potentialAction": {
            "@type": "SearchAction",
            "target": `${cleanBaseUrl}/shop?search={search_term_string}`,
            "query-input": "required name=search_term_string"
        }
    };

    let parsedSchema = finalSchema;
    if (typeof finalSchema === 'string') {
        try {
            parsedSchema = JSON.parse(finalSchema);
        } catch (e) {
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

            <title>{fullTitle}</title>
            <meta name="description" content={metaDesc} />
            {keywords && <meta name="keywords" content={keywords} />}
            <meta name="robots" content={robotsContent} />
            <meta name="theme-color" content="#ef4056" />

            <link rel="preconnect" href={cleanBaseUrl} crossOrigin="use-credentials" />
            <link rel="dns-prefetch" href={cleanBaseUrl} />
            {imageUrl && <link rel="preload" as="image" href={imageUrl} fetchPriority="high" />}

            {canonicalUrl && <link rel="canonical" href={canonicalUrl} />}

            <meta property="og:title" content={fullTitle} />
            <meta property="og:description" content={metaDesc} />
            <meta property="og:type" content={ogType} />
            {canonicalUrl && <meta property="og:url" content={canonicalUrl} />}
            <meta property="og:site_name" content={siteName} />
            <meta property="og:locale" content={ogLocale} />
            {imageUrl && <meta property="og:image" content={imageUrl} />}
            {imageUrl && <meta property="og:image:alt" content={fullTitle} />}
            <meta property="og:updated_time" content={modifiedAt} />

            <meta name="twitter:card" content={twitterCard} />
            <meta name="twitter:title" content={fullTitle} />
            <meta name="twitter:description" content={metaDesc} />
            {imageUrl && <meta name="twitter:image" content={imageUrl} />}
            {imageUrl && <meta name="twitter:image:alt" content={fullTitle} />}
            {twitterSite && <meta name="twitter:site" content={twitterSite} />}
            {twitterCreator && <meta name="twitter:creator" content={twitterCreator} />}

            <script type="application/ld+json">
                {JSON.stringify(compiledSchema)}
            </script>

            {!isArticle && price !== undefined && <meta property="product:price:amount" content={price.toString()} />}
            {!isArticle && price !== undefined && <meta property="product:price:currency" content="IRT" />}
            {!isArticle && inventory !== undefined && <meta property="product:availability" content={inventory > 0 ? "instock" : "oos"} />}
            {!isArticle && brand && <meta property="product:brand" content={brand} />}

            {isArticle && seoData.article_author && <meta property="article:author" content={seoData.article_author} />}
            {isArticle && <meta property="article:published_time" content={seoData.created_at || modifiedAt} />}
            {isArticle && <meta property="article:modified_time" content={modifiedAt} />}

            {!isArticle && productId && <meta name="product_id" content={productId} />}
            {!isArticle && metaTitle && <meta name="product_name" content={metaTitle} />}
            {!isArticle && price !== undefined && <meta name="product_price" content={price.toString()} />}
            {!isArticle && oldPrice !== undefined && <meta name="product_old_price" content={oldPrice.toString()} />}
            {!isArticle && inventory !== undefined && <meta name="availability" content={inventory > 0 ? "instock" : "outofstock"} />}
            {!isArticle && guarantee && <meta name="guarantee" content={guarantee} />}
        </Helmet>
    );
};

export default SeoMeta;