FROM odoo:20.0-20261112

USER root
COPY --chown=odoo:odoo odoo /opt/odoo-project/odoo
COPY --chown=odoo:odoo addons /opt/odoo-project/addons
COPY --chown=odoo:odoo custom_addons/ventas_unicah /mnt/extra-addons/ventas_unicah
COPY --chown=odoo:odoo odoo-bin render_start.py /opt/odoo-project/
RUN mkdir -p /var/lib/odoo && chown -R odoo:odoo /var/lib/odoo
USER odoo
WORKDIR /opt/odoo-project
ENV PYTHONUNBUFFERED=1
EXPOSE 10000
ENTRYPOINT ["python3", "/opt/odoo-project/render_start.py"]
