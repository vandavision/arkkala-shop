import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const DJANGO_INTERNAL_URL = process.env.DJANGO_INTERNAL_URL || 'http://django:8000';

const escapeHtml = (str = '') =>
  String(str || '')
    .replace(/&/g, '&' + 'amp;')
    .replace(/</g, '&' + 'lt;')
    .replace(/>/g, '&' + 'gt;')
    .replace(/"/g, '&' + 'quot;')
    .replace(/'/g, '&' + '#39;');

const stripHtml = (html = '') =>
  String(html || '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

function arkkalaSsrSeoPlugin() {
  return {
    name: 'arkkala-ssr-seo-plugin',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        try {
          const url = req.originalUrl || req.url || '/';
          const cleanPath = url.split('?')[0];

          if (
            req.method !== 'GET' ||
            cleanPath.startsWith('/api') ||
            cleanPath.startsWith('/media') ||
            cleanPath.startsWith('/src') ||
            cleanPath.startsWith('/@') ||
            cleanPath.startsWith('/node_modules') ||
            cleanPath.startsWith('/assets') ||
            /\.(js|jsx|ts|tsx|css|png|jpg|jpeg|gif|svg|webp|ico|woff|woff2|ttf|json|xml|txt|map)$/i.test(cleanPath)
          ) {
            return next();
          }

          const protocol = req.headers['x-forwarded-proto'] || 'http';
          const host = req.headers['x-forwarded-host'] || req.headers.host || '127.0.0.1:3000';
          const origin = `${protocol}://${host}`;

          const productMatch = cleanPath.match(/^\/product\/([^/]+)\/?$/);
          if (!productMatch) {
            return next();
          }

          const slug = decodeURIComponent(productMatch[1]);
          const apiRes = await fetch(
            `${DJANGO_INTERNAL_URL}/api/shop/products/${encodeURIComponent(slug)}/`,
            { headers: { Accept: 'application/json' } }
          );

          if (!apiRes.ok) {
            return next();
          }

          const product = await apiRes.json();
          const siteName = product?.seo?.og_site_name || 'ارک کالا';
          const title = product?.title || 'محصول';
          const fullTitle = title.includes(siteName) ? title : `${title} | ${siteName}`;
          const rawDesc =
            product?.seo?.meta_description ||
            product?.short_description ||
            stripHtml(product?.description) ||
            `خرید و قیمت ${title} در ${siteName}`;
          const metaDesc = rawDesc.length > 160 ? `${rawDesc.substring(0, 157)}...` : rawDesc;
          const canonicalUrl = `${origin}/product/${product.slug}`;

          const mainImgObj = product?.gallery?.find((g) => g.is_main) || product?.gallery?.[0];
          let imageUrl = mainImgObj?.url || product?.seo?.og_image_url || `${origin}/assets/image/logo.png`;
          if (imageUrl.startsWith('/')) {
            imageUrl = `${origin}${imageUrl}`;
          } else {
            imageUrl = imageUrl.replace(/^https?:\/\/[^/]+/i, origin);
          }

          const effectivePrice = String(product?.final_price ?? product?.base_price ?? 0);
          const inStock =
            (product?.base_inventory || 0) > 0 ||
            (product?.variants || []).some((v) => v.inventory > 0);

          const orgSchema = {
            '@type': 'Organization',
            '@id': `${origin}/#organization`,
            name: siteName,
            url: origin,
            logo: {
              '@type': 'ImageObject',
              url: `${origin}/assets/image/logo.png`,
            },
            sameAs: [
              'https://instagram.com/arkkala',
              'https://t.me/arkkala',
              'https://www.linkedin.com/company/arkkala',
            ],
            contactPoint: {
              '@type': 'ContactPoint',
              telephone: '+98-21-12345678',
              contactType: 'customer service',
              areaServed: 'IR',
              availableLanguage: ['Persian', 'fa'],
            },
          };

          const websiteSchema = {
            '@type': 'WebSite',
            '@id': `${origin}/#website`,
            name: siteName,
            url: origin,
            publisher: { '@id': `${origin}/#organization` },
            inLanguage: 'fa-IR',
            potentialAction: {
              '@type': 'SearchAction',
              target: {
                '@type': 'EntryPoint',
                urlTemplate: `${origin}/shop?search={search_term_string}`,
              },
              'query-input': 'required name=search_term_string',
            },
          };

          const backendGraph = Array.isArray(product?.seo?.schema_markup?.['@graph'])
            ? product.seo.schema_markup['@graph']
            : [];

          const normalizedBackendGraph = JSON.parse(
            JSON.stringify(backendGraph).replace(/https?:\/\/arkkala\.com/g, origin)
          );

          const compiledSchema = {
            '@context': 'https://schema.org',
            '@graph': [orgSchema, websiteSchema, ...normalizedBackendGraph],
          };

          const takeawaysList = Array.isArray(product?.key_takeaways) ? product.key_takeaways : [];
          const citationsList = Array.isArray(product?.citations) ? product.citations : [];
          const questionsList = Array.isArray(product?.questions) ? product.questions : [];
          const commentsList = Array.isArray(product?.comments) ? product.comments : [];

          req._ssrSeoPayload = {
            fullTitle,
            metaDesc,
            canonicalUrl,
            imageUrl,
            siteName,
            effectivePrice,
            inStock,
            compiledSchema,
            product,
            takeawaysList,
            citationsList,
            questionsList,
            commentsList,
          };

          return next();
        } catch (err) {
          return next();
        }
      });
    },
    transformIndexHtml(html, ctx) {
      const payload = ctx?.req?._ssrSeoPayload;
      if (!payload) return html;

      const {
        fullTitle,
        metaDesc,
        canonicalUrl,
        imageUrl,
        siteName,
        effectivePrice,
        inStock,
        compiledSchema,
        product,
        takeawaysList,
        citationsList,
        questionsList,
        commentsList,
      } = payload;

      const headTags = [
        `<title>${escapeHtml(fullTitle)}</title>`,
        `<meta name="description" content="${escapeHtml(metaDesc)}" />`,
        `<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" />`,
        `<link rel="canonical" href="${escapeHtml(canonicalUrl)}" />`,
        `<link rel="alternate" hreflang="fa-IR" href="${escapeHtml(canonicalUrl)}" />`,
        `<link rel="alternate" hreflang="x-default" href="${escapeHtml(canonicalUrl)}" />`,
        `<meta property="og:title" content="${escapeHtml(fullTitle)}" />`,
        `<meta property="og:description" content="${escapeHtml(metaDesc)}" />`,
        `<meta property="og:type" content="product" />`,
        `<meta property="og:url" content="${escapeHtml(canonicalUrl)}" />`,
        `<meta property="og:site_name" content="${escapeHtml(siteName)}" />`,
        `<meta property="og:locale" content="fa_IR" />`,
        `<meta property="og:image" content="${escapeHtml(imageUrl)}" />`,
        `<meta property="og:image:alt" content="${escapeHtml(fullTitle)}" />`,
        `<meta name="twitter:card" content="summary_large_image" />`,
        `<meta name="twitter:title" content="${escapeHtml(fullTitle)}" />`,
        `<meta name="twitter:description" content="${escapeHtml(metaDesc)}" />`,
        `<meta name="twitter:image" content="${escapeHtml(imageUrl)}" />`,
        `<meta property="product:price:amount" content="${escapeHtml(effectivePrice)}" />`,
        `<meta property="product:price:currency" content="IRT" />`,
        `<meta property="product:availability" content="${inStock ? 'instock' : 'oos'}" />`,
        `<meta name="product_id" content="${escapeHtml(product.uuid)}" />`,
        `<meta name="product_name" content="${escapeHtml(product.title)}" />`,
        `<meta name="product_price" content="${escapeHtml(effectivePrice)}" />`,
        `<meta name="availability" content="${inStock ? 'instock' : 'outofstock'}" />`,
        `<script id="ssr-json-ld" type="application/ld+json">${JSON.stringify(compiledSchema)}</script>`,
      ].join('\n    ');

      const ssrBodyHtml = `
      <main class="container py-4">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="/">خانه</a></li>
            <li class="breadcrumb-item"><a href="/shop">فروشگاه</a></li>
            ${
              product.category
                ? `<li class="breadcrumb-item"><a href="/category/${escapeHtml(product.category.slug)}">${escapeHtml(product.category.title)}</a></li>`
                : ''
            }
            <li class="breadcrumb-item active" aria-current="page">${escapeHtml(product.title)}</li>
          </ol>
        </nav>
        <article>
          <h1>${escapeHtml(product.title)}</h1>
          ${product.english_title ? `<p>${escapeHtml(product.english_title)}</p>` : ''}
          <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(product.title)}" width="400" height="400" />
          <div class="product-short-description">
            <p>${escapeHtml(product.short_description || metaDesc)}</p>
          </div>
          <p>قیمت: ${Number(effectivePrice).toLocaleString('fa-IR')} تومان | وضعیت: ${inStock ? 'موجود در انبار' : 'ناموجود'}</p>
          ${
            product.brand
              ? `<p>برند: <a href="/shop?brands=${escapeHtml(product.brand.slug)}">${escapeHtml(product.brand.title)}</a></p>`
              : ''
          }
          ${
            takeawaysList.length > 0
              ? `<section>
                  <h2>ویژگی‌های برتر</h2>
                  <ul class="key-takeaways-list">
                    ${takeawaysList.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}
                  </ul>
                </section>`
              : ''
          }
          <section>
            <h2>جزئیات و تب‌های اطلاعات کالا</h2>
            <h2>بررسی تخصصی و معرفی</h2>
            <div>${escapeHtml(stripHtml(product.description))}</div>
            ${product.expert_reviewer ? `<p>بررسی‌کننده تخصصی: ${escapeHtml(product.expert_reviewer)}</p>` : ''}
            ${
              citationsList.length > 0
                ? `<p>منابع و مراجع: ${citationsList.map((c) => escapeHtml(c)).join(' ، ')}</p>`
                : ''
            }
          </section>
          ${
            questionsList.length > 0
              ? `<section>
                  <h2>پرسش و پاسخ‌های متداول</h2>
                  ${questionsList
                    .map(
                      (q) =>
                        `<div><h3>${escapeHtml(q.text)}</h3><p>${escapeHtml(q.answer_text || '')}</p></div>`
                    )
                    .join('')}
                </section>`
              : ''
          }
          ${
            commentsList.length > 0
              ? `<section>
                  <h2>دیدگاه‌های کاربران</h2>
                  ${commentsList.map((c) => `<p>${escapeHtml(c.user_name)}: ${escapeHtml(c.body)}</p>`).join('')}
                </section>`
              : ''
          }
        </article>
      </main>`;

      return html
        .replace(/<title>.*?<\/title>/is, headTags)
        .replace('<div id="root"></div>', `<div id="root">${ssrBodyHtml}</div>`);
    },
  };
}

export default defineConfig({
  plugins: [react(), arkkalaSsrSeoPlugin()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: ['nginx', 'localhost', '127.0.0.1', true],
    hmr: {
      clientPort: 3000,
    },
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://django:8000',
        changeOrigin: false,
        secure: false,
      },
      '/media': {
        target: 'http://django:8000',
        changeOrigin: false,
      },
      '/sitemap.xml': {
        target: 'http://django:8000',
        changeOrigin: false,
      },
      '/robots.txt': {
        target: 'http://django:8000',
        changeOrigin: false,
      },
      '/llms.txt': {
        target: 'http://django:8000',
        changeOrigin: false,
      },
      '/llms-full.txt': {
        target: 'http://django:8000',
        changeOrigin: false,
      },
      '/llm.txt': {
        target: 'http://django:8000',
        changeOrigin: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['swiper', 'chart.js', 'rc-slider'],
          'utils-vendor': ['axios', 'react-helmet-async'],
        },
      },
    },
  },
});