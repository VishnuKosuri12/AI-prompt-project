FROM public.ecr.aws/nginx/nginx:1.27-alpine3.21-slim

# Create directory structure for static content
RUN mkdir -p /usr/share/nginx/html/static

# Copy static files
COPY styles.css /usr/share/nginx/html/static/
COPY search-styles.css /usr/share/nginx/html/static/
COPY chemical-details.css /usr/share/nginx/html/static/
COPY reports-styles.css /usr/share/nginx/html/static/
COPY covestro.png /usr/share/nginx/html/static/
COPY copyright.html /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
