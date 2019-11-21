import numpy

class OasysSurfaceData(object):
    def __init__(self,
                 xx=None,
                 yy=None,
                 zz=None,
                 surface_data_file=None):
        self.xx = xx
        self.yy = yy
        self.zz = zz
        self.surface_data_file=surface_data_file


class OasysErrorProfileData(object):

    def __init__(self,
                 surface_data=None,
                 error_profile_x_dim=0.0,
                 error_profile_y_dim=0.0):
        self.surface_data = surface_data
        self.error_profile_x_dim = error_profile_x_dim
        self.error_profile_y_dim = error_profile_y_dim

class OasysPreProcessorData(object):

    def __init__(self, error_profile_data=None, reflectivity_data=None):
        super().__init__()

        self.error_profile_data = error_profile_data
        self.reflectivity_data = reflectivity_data
        self.additional_data = None

    def set_additional_data(self, key, value):
        if self._additional_data is None:
            self._additional_data = {key : value}
        else:
            self._additional_data[key] = value

    def get_additional_data(self, key):
        return self._additional_data[key]

    def has_additional_data(self, key):
        return key in self._additional_data

class OasysThicknessErrorsData(object):
    def __init__(self, thickness_error_profile_data_files=[]):
        self.thickness_error_profile_data_files = thickness_error_profile_data_files
