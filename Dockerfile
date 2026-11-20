FROM odoo:20.0-20261112

USER root
RUN rm -rf /usr/lib/python3/dist-packages/odoo
COPY --chown=odoo:odoo odoo /opt/odoo-project/odoo
COPY --chown=odoo:odoo addons /opt/odoo-project/addons
COPY --chown=odoo:odoo custom_addons/ventas_unicah /mnt/extra-addons/ventas_unicah
COPY --chown=odoo:odoo odoo-bin render_start.py /opt/odoo-project/
RUN sed -i "s/elif self.url:/elif self.type == 'url' and self.url:/" /opt/odoo-project/odoo/addons/base/models/ir_attachment.py
RUN touch /opt/odoo-project/addons/web/static/src/scss/base_frontend.scss /opt/odoo-project/addons/web/static/src/public/lazyloader.js
RUN mkdir -p /var/lib/odoo && chown -R odoo:odoo /var/lib/odoo
USER odoo
WORKDIR /opt/odoo-project
ENV PYTHONUNBUFFERED=1
EXPOSE 10000
ENTRYPOINT ["python3", "/opt/odoo-project/render_start.py"]
