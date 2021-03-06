import pytest
import pandas

from nereid.src.treatment_facility.constructors import build_treatment_facility_nodes
from nereid.core.io import parse_configuration_logic


@pytest.mark.parametrize(
    "ctxt_key, has_met_data",
    [("default", True), ("default_api_no_tf_joins_valid", False)],
)
@pytest.mark.parametrize(
    "model, checkfor",
    [
        ("PermPoolFacility", "retention_volume_cuft"),
        ("RetAndTmntFacility", "retention_volume_cuft"),
        ("BioInfFacility", "retention_volume_cuft"),
        ("FlowAndRetFacility", "retention_volume_cuft"),
        ("RetentionFacility", "retention_volume_cuft"),
        ("TmntFacility", "treatment_volume_cuft"),
        ("CisternFacility", "design_storm_depth_inches"),  # TODO
        ("DryWellFacility", "retention_volume_cuft"),
        ("LowFlowFacility", "design_storm_depth_inches"),  # TODO
        ("FlowFacility", "design_storm_depth_inches"),  # TODO
        ("NTFacility", "design_storm_depth_inches"),
    ],
)
def test_build_treatment_facility_nodes(
    contexts, valid_treatment_facility_dicts, ctxt_key, has_met_data, model, checkfor
):

    context = contexts[ctxt_key]
    tmnt_facilities = pandas.DataFrame([valid_treatment_facility_dicts[model]])
    df, messages = parse_configuration_logic(
        df=pandas.DataFrame(tmnt_facilities),
        config_section="api_recognize",
        config_object="treatment_facility",
        context=context,
    )
    node = build_treatment_facility_nodes(df)[0]

    check_val = node.get(checkfor)
    assert isinstance(check_val, float)

    if has_met_data:
        assert node.get("rain_gauge") is not None
    else:
        assert node.get("rain_gauge") is None


@pytest.mark.parametrize(
    "ctxt_key, has_met_data",
    [("default", True), ("default_api_no_tf_joins_valid", False)],
)
def test_build_treatment_facility_nodes_from_long_list(
    contexts, valid_treatment_facilities, ctxt_key, has_met_data
):

    context = contexts[ctxt_key]
    tmnt_facilities = pandas.DataFrame(valid_treatment_facilities)
    df, messages = parse_configuration_logic(
        df=tmnt_facilities,
        config_section="api_recognize",
        config_object="treatment_facility",
        context=context,
    )
    nodes = build_treatment_facility_nodes(df)

    for n in nodes:
        if has_met_data:
            assert n.get("rain_gauge") is not None
        else:
            assert n.get("rain_gauge") is None
