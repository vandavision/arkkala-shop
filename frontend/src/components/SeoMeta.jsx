import React, { useEffect, useContext } from 'react';
import { Helmet } from 'react-helmet-async';
import { SiteContext } from '../context/SiteContext';

const SeoMeta = ({
    seoData,
    fallbackTitle,
    fallbackDescription,
    price,
    oldPrice,
    inventory,
    isArticle = false,
    isProduct = false,
    customImage,
    customSchema,
    slug,
    productId,
    guarantee = 'گارانتی اصالت و سلامت فیزیکی کالا',
    brand,
}) => {
    const siteCtx = useContext(SiteContext);
    const settings = siteCtx?.settings || {};

    const safeSeo = seoData && typeof seoData === 'object' ? seoData : {};
    const hasSeoContent = Boolean(
        Object.keys(safeSeo).length > 0 || fallbackTitle || fallbackDescription || customSchema
    );

    // Determine active origin dynamically so Canonical is always strictly self-referencing
    const getActiveOrigin = () => {
        if (typeof window !== 'undefined' && window.location?.origin) {
            const host = window.location.hostname;
            if (host !== 'nginx' && host !== 'django') {
                return window.location.origin.replace(/\/$/, '');
            }
        }
        return (import.meta.env.VITE_FRONTEND_URL || 'https://arkkala.com').replace(/\/$/, '');
    };

    const cleanBaseUrl = getActiveOrigin();
    const siteName = safeSeo.og_site_name || settings?.site_name || 'ارک کالا';
    const rawTitle = safeSeo.og_title || safeSeo.title || fallbackTitle || siteName;
    const fullTitle = rawTitle.includes(siteName) ? rawTitle : `${rawTitle} | ${siteName}`;

    let metaDesc =
        safeSeo.og_description ||
        safeSeo.meta_description ||
        safeSeo.short_description ||
        safeSeo.description ||
        fallbackDescription ||
        '';

    if (!metaDesc || metaDesc.trim() === '') {
        metaDesc = `${rawTitle} در فروشگاه اینترنتی ${siteName}. بررسی مشخصات، مقایسه تخصصی و خرید آنلاین با تضمین بهترین قیمت و اصالت کالا.`;
    } else if (metaDesc.length < 100) {
        metaDesc = `${metaDesc} | خرید آنلاین با تضمین اصالت کالا و بهترین قیمت در فروشگاه اینترنتی ${siteName}.`;
    }

    if (metaDesc.length > 160) {
        metaDesc = metaDesc.substring(0, 157) + '...';
    }

    const keywords = Array.isArray(safeSeo.seo_keywords)
        ? safeSeo.seo_keywords.join(', ')
        : safeSeo.seo_keywords || '';

    const isProductPage = isProduct || price !== undefined || Boolean(productId);
    const ogType = safeSeo.og_type || (isArticle ? 'article' : isProductPage ? 'product' : 'website');
    const ogLocale = safeSeo.og_locale || 'fa_IR';
    const robotsContent =
        safeSeo.robots || 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1';

    let currentPath = '/';
    if (typeof window !== 'undefined' && window.location?.pathname) {
        currentPath = window.location.pathname;
    } else if (slug) {
        currentPath = `${isArticle ? '/blog/' : isProductPage ? '/product/' : '/'}${slug}`;
    }

    const normalizedPath = currentPath === '/' ? '/' : currentPath.replace(/\/$/, '');
    const canonicalUrl = `${cleanBaseUrl}${normalizedPath}`;

    let imageUrl =
        customImage ||
        safeSeo.og_image_url ||
        safeSeo.image ||
        safeSeo.image_url ||
        settings?.logo_url ||
        '/assets/image/logo.png';

    if (imageUrl && imageUrl.startsWith('/')) {
        imageUrl = `${cleanBaseUrl}${imageUrl}`;
    } else if (imageUrl) {
        imageUrl = imageUrl.replace(/^https?:\/\/[^/]+/i, cleanBaseUrl);
    }

    const twitterCard = safeSeo.twitter_card || 'summary_large_image';
    const twitterSite = safeSeo.twitter_site || '@arkkala';
    const twitterCreator = safeSeo.twitter_creator || '';

    const configuredSocials = [
        settings?.instagram,
        settings?.telegram,
        settings?.linkedin,
        settings?.twitter,
        settings?.whatsapp,
    ].filter((link) => link && typeof link === 'string' && link.startsWith('http'));

    const sameAsLinks =
        configuredSocials.length > 0
            ? configuredSocials
            : [
                  'https://instagram.com/arkkala',
                  'https://t.me/arkkala',
                  'https://www.linkedin.com/company/arkkala',
              ];

    const orgSchema = {
        '@type': 'Organization',
        '@id': `${cleanBaseUrl}/#organization`,
        name: siteName,
        url: cleanBaseUrl,
        logo: {
            '@type': 'ImageObject',
            url: settings?.logo_url || `${cleanBaseUrl}/assets/image/logo.png`,
        },
        sameAs: sameAsLinks,
        contactPoint: {
            '@type': 'ContactPoint',
            telephone: settings?.phone_number || '+98-21-12345678',
            contactType: 'customer service',
            areaServed: 'IR',
            availableLanguage: ['Persian', 'fa'],
        },
    };

    const websiteSchema = {
        '@type': 'WebSite',
        '@id': `${cleanBaseUrl}/#website`,
        name: siteName,
        url: cleanBaseUrl,
        publisher: { '@id': `${cleanBaseUrl}/#organization` },
        inLanguage: 'fa-IR',
        potentialAction: {
            '@type': 'SearchAction',
            target: {
                '@type': 'EntryPoint',
                urlTemplate: `${cleanBaseUrl}/shop?search={search_term_string}`,
            },
            'query-input': 'required name=search_term_string',
        },
    };

    const rawSchema = customSchema || safeSeo.schema_markup || safeSeo.json_ld;
    let parsedSchema = rawSchema;
    if (typeof rawSchema === 'string') {
        try {
            parsedSchema = JSON.parse(rawSchema);
        } catch {
            parsedSchema = null;
        }
    }

    let schemaGraph = [orgSchema, websiteSchema];
    if (parsedSchema && typeof parsedSchema === 'object') {
        const normalizedParsed = JSON.parse(
            JSON.stringify(parsedSchema).replace(/https?:\/\/arkkala\.com/g, cleanBaseUrl)
        );
        if (Array.isArray(normalizedParsed['@graph'])) {
            const filteredGraph = normalizedParsed['@graph'].filter(
                (node) => node['@type'] !== 'Organization' && node['@type'] !== 'WebSite'
            );
            schemaGraph = [...schemaGraph, ...filteredGraph];
        } else if (Object.keys(normalizedParsed).length > 0) {
            const { '@context': _, ...restSchema } = normalizedParsed;
            if (
                Object.keys(restSchema).length > 0 &&
                restSchema['@type'] !== 'Organization' &&
                restSchema['@type'] !== 'WebSite'
            ) {
                schemaGraph.push(restSchema);
            }
        }
    }

    const compiledSchema = {
        '@context': 'https://schema.org',
        '@graph': schemaGraph,
    };

    const serializedSchema = JSON.stringify(compiledSchema);

    useEffect(() => {
        if (typeof window === 'undefined' || !hasSeoContent) return;

        // Deduplicate any extra JSON-LD scripts rendered by child pages so only ONE exists
        const allJsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
        let primaryScript = document.getElementById('ssr-json-ld');

        if (!primaryScript && allJsonLdScripts.length > 0) {
            primaryScript = allJsonLdScripts[0];
            primaryScript.id = 'ssr-json-ld';
        }

        allJsonLdScripts.forEach((scriptEl) => {
            if (scriptEl !== primaryScript) {
                scriptEl.remove();
            }
        });

        if (primaryScript) {
            primaryScript.removeAttribute('data-rh');
            if (primaryScript.textContent !== serializedSchema) {
                primaryScript.textContent = serializedSchema;
            }
        }

        const timer = setTimeout(() => {
            window.prerenderReady = true;
        }, 50);

        return () => clearTimeout(timer);
    }, [hasSeoContent, serializedSchema, canonicalUrl]);

    if (!hasSeoContent) return null;

    const modifiedAt = safeSeo.modified_at || safeSeo.created_at || new Date().toISOString();
    const effectivePrice = inventory > 0 && price !== undefined ? price : 0;
    const hasSsrScript = typeof document !== 'undefined' && Boolean(document.getElementById('ssr-json-ld'));

    return (
        <Helmet>
            <html lang="fa" dir="rtl" />

            <title>{fullTitle}</title>
            <meta name="description" content={metaDesc} />
            {keywords && <meta name="keywords" content={keywords} />}
            <meta name="robots" content={robotsContent} />
            <meta name="googlebot" content={robotsContent} />
            <meta name="bingbot" content={robotsContent} />
            <meta name="theme-color" content="#ef4056" />

            <link rel="canonical" href={canonicalUrl} />
            <link rel="alternate" hrefLang="fa-IR" href={canonicalUrl} />
            <link rel="alternate" hrefLang="x-default" href={canonicalUrl} />

            {/* OpenGraph Metadata */}
            <meta property="og:title" content={fullTitle} />
            <meta property="og:description" content={metaDesc} />
            <meta property="og:type" content={ogType} />
            <meta property="og:url" content={canonicalUrl} />
            <meta property="og:site_name" content={siteName} />
            <meta property="og:locale" content={ogLocale} />
            {imageUrl && <meta property="og:image" content={imageUrl} />}
            {imageUrl && <meta property="og:image:alt" content={fullTitle} />}
            <meta property="og:updated_time" content={modifiedAt} />

            {/* Twitter Card Metadata */}
            <meta name="twitter:card" content={twitterCard} />
            <meta name="twitter:title" content={fullTitle} />
            <meta name="twitter:description" content={metaDesc} />
            {imageUrl && <meta name="twitter:image" content={imageUrl} />}
            {imageUrl && <meta name="twitter:image:alt" content={fullTitle} />}
            {twitterSite && <meta name="twitter:site" content={twitterSite} />}
            {twitterCreator && <meta name="twitter:creator" content={twitterCreator} />}

            {/* GEO / E-E-A-T Signals */}
            {safeSeo.expert_reviewer && <meta name="author" content={safeSeo.expert_reviewer} />}
            {safeSeo.expert_reviewer && <meta name="reviewed-by" content={safeSeo.expert_reviewer} />}
            {Array.isArray(safeSeo.citations) && safeSeo.citations.length > 0 && (
                <meta name="citation_reference" content={safeSeo.citations.join(' | ')} />
            )}

            {/* Product & Shopping Bots Meta Tags */}
            {isProductPage && price !== undefined && (
                <meta property="product:price:amount" content={String(effectivePrice)} />
            )}
            {isProductPage && price !== undefined && <meta property="product:price:currency" content="IRT" />}
            {isProductPage && inventory !== undefined && (
                <meta property="product:availability" content={inventory > 0 ? 'instock' : 'oos'} />
            )}
            {isProductPage && brand && <meta property="product:brand" content={brand} />}

            {isProductPage && productId && <meta name="product_id" content={String(productId)} />}
            {isProductPage && rawTitle && <meta name="product_name" content={rawTitle} />}
            {isProductPage && price !== undefined && (
                <meta name="product_price" content={String(effectivePrice)} />
            )}
            {isProductPage && oldPrice !== undefined && Number(oldPrice) > Number(effectivePrice) && (
                <meta name="product_old_price" content={String(oldPrice)} />
            )}
            {isProductPage && inventory !== undefined && (
                <meta name="availability" content={inventory > 0 ? 'instock' : 'outofstock'} />
            )}
            {isProductPage && guarantee && <meta name="guarantee" content={guarantee} />}

            {/* Only render via Helmet if SSR script wasn't already injected */}
            {!hasSsrScript && (
                <script id="ssr-json-ld" type="application/ld+json">
                    {serializedSchema}
                </script>
            )}
        </Helmet>
    );
};

export default SeoMeta;