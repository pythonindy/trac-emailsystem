#!/usr/bin/env python

from setuptools import setup

setup(
    name='TracEmailSystem',
    version='0.12.0.1',
    packages=['tracext', 'tracext.emailsystem'],
    namespace_packages=['tracext'],
    entry_points = {'trac.plugins': [
        'emailsystem.api = tracext.emailsystem.api',
        'emailsystem.provider.imap = tracext.emailsystem.provider.imap',
        'emailsystem.processor.ticket = tracext.emailsystem.processor.ticket',
        ]},
)