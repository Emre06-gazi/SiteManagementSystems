from flask.views import MethodView
from project.modules import modules
from json import dumps

deviceDatas = {
    "Bran Sitesi": {
        "A Bolgesi":
            {
            "Sulama": {
                "b8d61ab24ee8": {
                    "name": "İlk efendi",
                    "status": "connected",
                    "slaves": {
                        "0": False,
                        "1": True
                    },
                    "activeGroup": "Plan A"
                }
            },
            "Elektrik": {
                "c8f09e9e2088": {
                    "name": "İlk efendi",
                    "status": "connected",
                    "slaves": {
                        "0": False,
                        "1": True
                    },
                    "activeGroup": "Plan A"
                }
            }
        },
        "B Bolgesi":
            {
            "Sulama": {
                "b8d61ab24ee8": {
                    "name": "İlk efendi",
                    "status": "connected",
                    "slaves": {
                        "0": False,
                        "1": True
                    },
                    "activeGroup": "Plan A"
                }
            },
            "Elektrik": {
                "b8d61ab24ee8": {
                    "name": "İlk efendi",
                    "status": "connected",
                    "slaves": {
                        "0": False,
                        "1": True
                    },
                    "activeGroup": "Plan A"
                }
            }
        }
    },
    "Akin Sitesi": {
        "Ana Bolge": {
            "Sulama": {
                "1234567890ab": {
                    "name": "Akin Efendi",
                    "status": "connected",
                    "slaves": {
                        "0": True,
                        "1": False
                    },
                    "activeGroup": "Plan B"
                }
            },
            "Işıklandırma": {
                "1234567890b": {
                    "name": "Akin Efendi",
                    "status": "connected",
                    "slaves": {
                        "0": True,
                        "1": False
                    },
                    "activeGroup": "Plan B"
                }
            },
            "Elektrik": {
                "1234567890ab": {
                    "name": "Akin Efendi",
                    "status": "connected",
                    "slaves": {
                        "0": True,
                        "1": False
                    },
                    "activeGroup": "Plan B"
                }

            }
        },
        "Yan Bolge": {
            "Isitma Sistemi": {
                "1234567890ab": {
                    "name": "Akin Efendi",
                    "status": "connected",
                    "slaves": {
                        "0": True,
                        "1": False
                    },
                    "activeGroup": "Plan B"
                }
            },
            "Havalandirma Sistemi": {
                "1234567890ab": {
                    "name": "Akin Efendi",
                    "status": "connected",
                    "slaves": {
                        "0": True,
                        "1": False
                    },
                    "activeGroup": "Plan B"
                }
            },
        }
    },
    "Emre Sitesi": {
        "Bolge 1": {
            "Sulama": {
                "1234561890ab": {
                    "name": "Emre Efendi",
                    "status": "connected",
                    "slaves": {
                        "0": True,
                        "1": False
                    },
                    "activeGroup": "Plan C"
                }
            },
            "Havuz Havalandirma": {
                "1234561890ab": {
                    "name": "Emre Efendi",
                    "status": "connected",
                    "slaves": {
                        "0": True,
                        "1": False
                    },
                    "activeGroup": "Plan C"
                }
            }
        },
        "Bolge 2": {
                    "Sulama": {
                        "1234561890ab": {
                            "name": "Emre Efendi",
                            "status": "connected",
                            "slaves": {
                                "0": True,
                                "1": False
                            },
                            "activeGroup": "Plan C"
                        }
                    }
                }
    }
    ,
    "Omer Sitesi": {
        "Site Geneli Omer": {
            "Sulama": {
                "1234561890sb": {
                    "name": "Emre Efendi",
                    "status": "connected",
                    "slaves": {
                        "0": True,
                        "1": False
                    },
                    "activeGroup": "Plan C"
                }
            }
        }
    }
}


class SystemAPI(MethodView):
    init_every_request = False

    def __init__(self):
        ...

    def get(self, site=None, apartment=None, dType=None, device_id=None):

        if site is None:
            return dumps(list(deviceDatas.keys()))

        ret = deviceDatas.get(site, {})
        if apartment is None:
            return dumps(list(ret.keys()))

        ret = deviceDatas.get(site, {}).get(apartment, {})
        if dType is None:
            return dumps(list(ret.keys()))

        ret = deviceDatas.get(site, {}).get(apartment, {}).get(dType, {})
        if device_id is None:
            if ret:
                ret = {x: {"status": y.get("status", "unknown"), "name": y.get("name", "unknown")} for x, y in ret.items()}
            return dumps(ret)

        ret = deviceDatas.get(site, {}).get(apartment, {}).get(dType, {}).get(device_id, {})
        if ret:
            return dumps(ret)

    def patch(self, site=None, apartment=None, dType=None, device_id=None):
        return "OK"

    def delete(self, site=None, apartment=None, dType=None, device_id=None):
        return "OK"

    def update(self, site=None, apartment=None, dType=None, device_id=None):
        return "OK"


modules.app.add_url_rule(f"/api/treeView/<string:site>/<string:apartment>/<string:dType>/<string:device_id>", view_func=SystemAPI.as_view("api4"))
modules.app.add_url_rule(f"/api/treeView/<string:site>/<string:apartment>/<string:dType>", view_func=SystemAPI.as_view(f"api3"))
modules.app.add_url_rule(f"/api/treeView/<string:site>/<string:apartment>", view_func=SystemAPI.as_view(f"api2"))
modules.app.add_url_rule(f"/api/treeView/<string:site>", view_func=SystemAPI.as_view(f"api1"))
modules.app.add_url_rule(f"/api/treeView/", view_func=SystemAPI.as_view(f"api0"))
