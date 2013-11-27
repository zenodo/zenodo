# -*- coding: utf-8 -*-
#
## This file is part of ZENODO.
## Copyright (C) 2012, 2013 CERN.
##
## ZENODO is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## ZENODO is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with ZENODO. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

from invenio.dataciteutils import DataCite, HttpError, DataCiteError
from invenio.config import CFG_DATACITE_DOI_PREFIX


class PidProvider(object):
    """
    Abstract class for persistent identifier provider classes.

    Subclasses must implement register, update, delete and is_provider_for_pid
    methods and register itself:

        class MyProvider(PidProvider):
            pid_type = "mypid"

            def reserve(self, pid, *args, **kwargs):
                return True

            def register(self, pid, *args, **kwargs):
                return True

            def update(self, pid, *args, **kwargs):
                return True

            def delete(self, pid, *args, **kwargs):
                try:
                    ...
                except Exception, e:
                    pid.log("DELETE","Deletion failed")
                    return False
                else:
                    pid.log("DELETE","Successfully deleted")
                    return True

            def is_provider_for_pid(self, pid_str):
                pass

        PidProvider.register_provider(MyProvider)


    The provider is responsible for handling of errors, as well as logging of
    actions happening to the pid. See example above as well as the
    DataCitePidProvider.

    Each method takes variable number of argument and keywords arguments. This
    can be used to pass additional information to the provider when registering
    a persistent identifier. E.g. a DOI requires URL and metadata to be able
    to register the DOI.
    """

    registry = {}
    """ Registry of possible providers """

    pid_type = None
    """ Must be overwritten in subcleass and specified as a string (max len 6) """

    @staticmethod
    def register_provider(provider):
        """
        Register a new persistent identifier provider
        """
        if not issubclass(provider, PidProvider):
            raise TypeError("Argument not an instance of PidProvider.")
        pid_type = getattr(provider, 'pid_type', None)
        if pid_type is None:
            raise AttributeError(
                "Provider must specify class variable pid_type."
            )
        pid_type = pid_type.lower()
        if pid_type not in PidProvider.registry:
            PidProvider.registry[pid_type] = []

        # Prevent double registration
        if provider not in PidProvider.registry[pid_type]:
            PidProvider.registry[pid_type].append(provider)

    @staticmethod
    def create(pid_type, pid_str, *args, **kwargs):
        """
        Create a new instance of a PidProvider for the
        given type and pid.
        """
        providers = PidProvider.registry.get(pid_type.lower(), None)
        for p in providers:

            if p.is_provider_for_pid(pid_str):
                return p(*args, **kwargs)
        return None

    #
    # API methods which must be implemented by each provider.
    #
    def reserve(self, pid, *args, **kwargs):
        """
        Reserve a new persistent identifier

        This might or might not be useful depending on the service of the
        provider.
        """
        raise NotImplementedError

    def register(self, pid, *args, **kwargs):
        """ Register a new persistent identifier """
        raise NotImplementedError

    def update(self, pid, *args, **kwargs):
        """ Update information about a persistent identifier """
        raise NotImplementedError

    def delete(self, pid, *args, **kwargs):
        """ Delete a persistent identifier """
        raise NotImplementedError

    @classmethod
    def is_provider_for_pid(cls, pid_str):
        raise NotImplementedError


class LocalPidProvider(PidProvider):
    """
    Abstract class for local persistent identifier provides (i.e locally
    unmanaged DOIs).
    """
    def reserve(self, pid, *args, **kwargs):
        pid.log("RESERVE", "Successfully reserved locally")
        return True

    def register(self, pid, *args, **kwargs):
        pid.log("REGISTER", "Successfully registered in locally")
        return True

    def update(self, pid, *args, **kwargs):
        # No logging necessary as status of PID is not changing
        return True

    def delete(self, pid, *args, **kwargs):
        """ Delete a registered DOI """
        pid.log("DELETE", "Successfully deleted locally")
        return True


#
# DataCite PID provider
#
class DataCitePidProvider(PidProvider):
    """
    DOI provider using DataCite API.
    """
    pid_type = 'doi'

    def __init__(self):
        self.api = DataCite()

    def _get_url(self, kwargs):
        try:
            return kwargs['url']
        except KeyError:
            raise Exception("url keyword argument must be specified.")

    def _get_doc(self, kwargs):
        try:
            return kwargs['doc']
        except KeyError:
            raise Exception("doc keyword argument must be specified.")

    def reserve(self, pid, *args, **kwargs):
        """ Reserve a DOI (amounts to upload metadata, but not to mint) """
        # Only registered PIDs can be updated.
        doc = self._get_doc(kwargs)

        try:
            self.api.metadata_post(doc)
        except DataCiteError, e:
            pid.log("RESERVE", "Failed with %s" % e.__class__.__name__)
            return False
        except HttpError, e:
            pid.log("RESERVE", "Failed with HttpError - %s" % unicode(e))
            return False
        else:
            pid.log("RESERVE", "Successfully reserved in DataCite")
        return True

    def register(self, pid, *args, **kwargs):
        """ Register a DOI via the DataCite API """
        url = self._get_url(kwargs)
        doc = self._get_doc(kwargs)

        try:
            # Set metadata for DOI
            self.api.metadata_post(doc)
            # Mint DOI
            self.api.doi_post(pid.pid, url)
        except DataCiteError, e:
            pid.log("REGISTER", "Failed with %s" % e.__class__.__name__)
            return False
        except HttpError, e:
            pid.log("REGISTER", "Failed with HttpError - %s" % unicode(e))
            return False
        else:
            pid.log("REGISTER", "Successfully registered in DataCite")
        return True

    def update(self, pid, *args, **kwargs):
        """
        Update metadata associated with a DOI.

        This can be called before/after a DOI is registered

        """
        url = self._get_url(kwargs)
        doc = self._get_doc(kwargs)

        if pid.is_deleted():
            pid.log("UPDATE", "Reactivate in DataCite")

        try:
            # Set metadata
            self.api.metadata_post(doc)
            self.api.doi_post(pid.pid, url)
        except DataCiteError, e:
            pid.log("UPDATE", "Failed with %s" % e.__class__.__name__)
            return False
        except HttpError, e:
            pid.log("UPDATE", "Failed with HttpError - %s" % unicode(e))
            return False
        else:
            if pid.is_deleted():
                pid.log("UPDATE", "Successfully updated and possibly registered in DataCite")
            else:
                pid.log("UPDATE", "Successfully updated in DataCite")
        return True

    def delete(self, pid, *args, **kwargs):
        """ Delete a registered DOI """
        try:
            self.api.metadata_delete(pid.pid)
        except DataCiteError, e:
            pid.log("DELETE", "Failed with %s" % e.__class__.__name__)
            return False
        except HttpError, e:
            pid.log("DELETE", "Failed with HttpError - %s" % unicode(e))
            return False
        else:
            pid.log("DELETE", "Successfully deleted in DataCite")
        return True

    @classmethod
    def is_provider_for_pid(cls, pid_str):
        """
        Check if DataCite is the provider for this DOI

        Note: If you e.g. changed DataCite account and received a new prefix,
        then this provider can only update and register DOIs for the new
        prefix.
        """
        return pid_str.startswith("%s/" % CFG_DATACITE_DOI_PREFIX)


class LocalDOIProvider(LocalPidProvider):
    """
    Provider for locally unmanaged DOIs.
    """
    pid_type = 'doi'

    @classmethod
    def is_provider_for_pid(cls, pid_str):
        """
        Check if DOI is not the local datacite managed one.
        """
        return not pid_str.startswith("%s/" % CFG_DATACITE_DOI_PREFIX)


# Register the DataCite DOI provider
PidProvider.register_provider(DataCitePidProvider)
PidProvider.register_provider(LocalDOIProvider)
