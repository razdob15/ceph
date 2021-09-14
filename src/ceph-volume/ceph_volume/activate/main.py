# -*- coding: utf-8 -*-

import argparse

from ceph_volume import terminal
from ceph_volume.devices.lvm.activate import Activate as LVMActivate
from ceph_volume.devices.raw.activate import Activate as RAWActivate
from ceph_volume.devices.simple.activate import Activate as SimpleActivate
from ceph_volume.api.lvm import is_lvm_prepared_osd, get_objectstore_from_osd_id


class Activate(object):

    help = "Activate an OSD"

    def __init__(self, argv):
        self.argv = argv

    def main(self):
        parser = argparse.ArgumentParser(
            prog='ceph-volume activate',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=self.help,
        )
        parser.add_argument(
            '--osd-id',
            help='OSD ID to activate'
        )
        parser.add_argument(
            '--osd-uuid',
            help='OSD UUID to active'
        )
        parser.add_argument(
            '--no-systemd',
            dest='no_systemd',
            action='store_true',
            help='Skip creating and enabling systemd units and starting OSD services'
        )
        parser.add_argument(
            '--no-tmpfs',
            action='store_true',
            help='Do not use a tmpfs mount for OSD data dir'
        )
        self.args = parser.parse_args(self.argv)

        if not (self.args.osd_id or self.args.osd_uuid):
            parser.print_help()
            terminal.error('Either --osd-id or --osd-uuid must be provided.')
            raise SystemExit(1)

        # First, try to activate lvm osd
        lv = is_lvm_prepared_osd(osd_id=self.args.osd_id, osd_uuid=self.args.osd_uuid)

        if lv and get_objectstore_from_osd_id(self.args.osd_id) == 'filestore' and not self.args.osd_uuid: ### TODO: What if --osd-id isn't passed?
            raise RuntimeError('Filestore osds require --osd-uuid parameter.')

        # LVMActivate([]).activate() will fail if --osd-id *and* --osd-uuid aren't passed
        if lv and self.args.osd_uuid and self.args.osd_id:
            terminal.info('Activating LVM osd {}'.format(self.args.osd_id))
            LVMActivate([]).activate(
                argparse.Namespace(
                    osd_id=self.args.osd_id,
                    osd_fsid=self.args.osd_uuid,
                    no_tmpfs=self.args.no_tmpfs,
                    no_systemd=self.args.no_systemd,
                )
            )
            return

        # If it's not an lvm osd, let's try raw.
        # it can also activate bluestore osds
        # prepared with lvm when --osd-uuid isn't passed.
        try:
            RAWActivate([]).activate(
                devs=None,
                start_osd_id=self.args.osd_id,
                start_osd_uuid=self.args.osd_uuid,
                tmpfs=not self.args.no_tmpfs,
                systemd=not self.args.no_systemd,
            )
            return
        except Exception as e:
            terminal.info(f'Failed to activate via raw: {e}')

        # finally try simple
        try:
            SimpleActivate([]).activate(
                argparse.Namespace(
                    osd_id=self.args.osd_id,
                    osd_fsid=self.args.osd_uuid,
                    no_systemd=self.args.no_systemd,
                )
            )
            return
        except Exception as e:
            terminal.info(f'Failed to activate via simple: {e}')

        terminal.error('Failed to activate any OSD(s)')
