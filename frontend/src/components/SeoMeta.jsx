import React from 'react';
import { Helmet } from 'react-helmet-async';

const SeoMeta = ({ seoData, title, price }) => {
    if (!seoData) return null;
    const metaTitle = seoData.meta_title || title;
    
    return (
        <Helmet>
            <title>{metaTitle} | ارک کالا</title>
            <meta name="description" content={seoData.meta_description} />
            <link rel="canonical" href={seoData.canonical_url} />

            <meta property="og:title" content={metaTitle} />
            <meta property="og:description" content={seoData.meta_description} />
            <meta property="og:type" content="product" />
            <meta property="og:url" content={seoData.canonical_url} />
            <meta property="og:site_name" content="ارک کالا" />
            {seoData.og_image_url && <meta property="og:image" content={seoData.og_image_url} />}

            <meta property="product:price:amount" content={price} />
            <meta property="product:price:currency" content="IRT" />
            <meta property="product:availability" content="instock" />

            {seoData.json_ld && (
                <script type="application/ld+json">
                    {JSON.stringify(seoData.json_ld)}
                </script>
            )}
        </Helmet>
    );
};

export default SeoMeta;