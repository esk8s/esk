import base64
import copy
from injector.initcontainer import InitContainer
import re

from flask import current_app
from jsonpatch import JsonPatch


__INJECTION_ANNOTATION = "secrets.esk.io/inject-bindings"
__INJECTION_TEMPLATE_ANNOTATION = "secrets.esk.io/inject-template-([\w\-\_]+)"
__INJECTION_TARGET_ANNOTATION = "secrets.esk.io/inject-target-([\w\-\_]+)"
__INIT_FIRST_ANNOTATION = "secrets.esk.io/init-first"
__SKIP_ANNOTATION = "secrets.esk.io/injected"

__DEFAULT_VOLUME = {"name": "esk-secrets", "emptyDir": {}}

with open("/etc/podinfo/namespace", "r") as f:
    __DEFAULT_NAMESPACE = f.read().strip()


def get_bind_names_from_annotations(annotations):
    inject_bindings = {}
    inject_binding_templates = {}
    inject_binding_targets = {}

    for annotation_name, annotation_value in annotations.items():

        if annotation_name == __INJECTION_ANNOTATION:
            inject_bindings = annotation_value.split(",")
            continue

        template_inject_match = re.match(
            rf"{ __INJECTION_TEMPLATE_ANNOTATION }", annotation_name
        )
        if template_inject_match:
            inject_binding_templates[template_inject_match.group(1)] = annotation_value
            continue

        target_inject_match = re.match(
            rf"{ __INJECTION_TARGET_ANNOTATION }", annotation_name
        )
        if target_inject_match:
            inject_binding_targets[target_inject_match.group(1)] = annotation_value
            continue

    return [
        {
            "name": bind,
            "obj": None,
            "template": inject_binding_templates.get(bind),
            "target": inject_binding_targets.get(bind),
        }
        for bind in inject_bindings
    ]


def should_mutate(annotations):
    if annotations is None:
        return False

    return (
        annotations.get(__SKIP_ANNOTATION) is None
        or annotations.get(__SKIP_ANNOTATION).lower() != "true"
    )


def mutate(engine, init_image, processor_addr, req):
    if req["operation"] != "CREATE" or not should_mutate(
        req["object"]["metadata"]["annotations"]
    ):
        return True, ""

    req_obj = copy.deepcopy(req).get("object")

    raw_binds = get_bind_names_from_annotations(
        req_obj.get("metadata").get("annotations")
    )
    if len(raw_binds) == 0:
        return True, ""

    initContainer = InitContainer("esk-init", init_image, processor_addr)

    use_default_volume = False
    for bind in raw_binds:
        spec = engine.get_object_spec(
            bind.get("name"), req.get("namespace") or __DEFAULT_NAMESPACE, "secretbindings"
        ).get("spec")

        current_app.logger.debug(bind)

        if bind.get("target") is None:
            bind["target"] = spec.get("target")

        use_default_volume = use_default_volume or bind.get("target").startswith(
            "/esk/secrets"
        )

        initContainer.add_bind(bind, req.get("namespace"), spec)

    renderedContainer = initContainer.get()
    # Add our init container
    if "initContainers" not in req_obj["spec"]:
        req_obj["spec"]["initContainers"] = [renderedContainer]
    elif req_obj.get("metadata").get("annotations").get(__INIT_FIRST_ANNOTATION):
        # Add volumeMounts to every container

        for index in range(0, len(req_obj["spec"]["initContainers"])):
            if "volumeMounts" not in req_obj["spec"]["initContainers"][index]:
                req_obj["spec"]["initContainers"][index]["volumeMounts"] = []

            req_obj["spec"]["initContainers"][index][
                "volumeMounts"
            ] += renderedContainer.get("volumeMounts")

        req_obj["spec"]["initContainers"] = [renderedContainer] + req_obj["spec"][
            "initContainers"
        ]
    else:
        req_obj["spec"]["initContainers"].append(renderedContainer)

    pod_vols = initContainer.get_volumes()
    if use_default_volume:
        pod_vols.append(__DEFAULT_VOLUME)

    # Add our secret volumes
    if "volumes" not in req_obj["spec"]:
        req_obj["spec"]["volumes"] = pod_vols
    else:
        req_obj["spec"]["volumes"] += pod_vols

    # Add volumeMounts to every container
    for index in range(0, len(req_obj["spec"]["containers"])):
        if "volumeMounts" not in req_obj["spec"]["containers"][index]:
            req_obj["spec"]["containers"][index]["volumeMounts"] = []

        req_obj["spec"]["containers"][index]["volumeMounts"] += renderedContainer.get(
            "volumeMounts"
        )

    patch = JsonPatch.from_diff(req["object"], req_obj)

    return True, base64.b64encode(str(patch).encode()).decode()
