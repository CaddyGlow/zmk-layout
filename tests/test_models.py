"""Basic tests for ZMK layout models."""

from datetime import datetime

import pytest

from zmk_layout.models import (
    ComboBehavior,
    HoldTapBehavior,
    LayoutBaseModel,
    LayoutBinding,
    LayoutData,
    LayoutLayer,
    LayoutParam,
)


class TestLayoutBaseModel:
    """Test the base model functionality."""

    def test_create_instance(self):
        """Test creating a base model instance."""

        class TestModel(LayoutBaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42

    def test_to_dict(self):
        """Test dictionary conversion."""

        class TestModel(LayoutBaseModel):
            name: str
            value: int

        model = TestModel(name="test", value=42)
        result = model.to_dict()
        assert result == {"name": "test", "value": 42}

    def test_from_dict(self):
        """Test creating from dictionary."""

        class TestModel(LayoutBaseModel):
            name: str
            value: int

        data = {"name": "test", "value": 42}
        model = TestModel.from_dict(data)
        assert model.name == "test"
        assert model.value == 42


class TestLayoutParam:
    """Test LayoutParam model."""

    def test_create_simple_param(self):
        """Test creating simple parameter."""
        param = LayoutParam(value="Q")
        assert param.value == "Q"
        assert param.params == []

    def test_create_nested_param(self):
        """Test creating nested parameter."""
        inner = LayoutParam(value="X")
        outer = LayoutParam(value="LC", params=[inner])
        assert outer.value == "LC"
        assert len(outer.params) == 1
        assert outer.params[0].value == "X"


class TestLayoutBinding:
    """Test LayoutBinding model."""

    def test_create_simple_binding(self):
        """Test creating simple binding."""
        binding = LayoutBinding(value="&kp", params=[LayoutParam(value="Q")])
        assert binding.value == "&kp"
        assert len(binding.params) == 1
        assert binding.params[0].value == "Q"

    def test_from_str_simple(self):
        """Test parsing simple behavior string."""
        binding = LayoutBinding.from_str("&kp Q")
        assert binding.value == "&kp"
        assert len(binding.params) == 1
        assert binding.params[0].value == "Q"

    def test_from_str_no_params(self):
        """Test parsing behavior with no parameters."""
        binding = LayoutBinding.from_str("&trans")
        assert binding.value == "&trans"
        assert binding.params == []

    def test_from_str_multiple_params(self):
        """Test parsing behavior with multiple parameters."""
        binding = LayoutBinding.from_str("&mt LCTRL A")
        assert binding.value == "&mt"
        assert len(binding.params) == 2
        assert binding.params[0].value == "LCTRL"
        assert binding.params[1].value == "A"

    def test_from_str_nested_params(self):
        """Test parsing behavior with nested parameters."""
        binding = LayoutBinding.from_str("&kp LC(X)")
        assert binding.value == "&kp"
        assert len(binding.params) == 1
        assert binding.params[0].value == "LC"
        assert len(binding.params[0].params) == 1
        assert binding.params[0].params[0].value == "X"

    def test_from_str_empty_raises_error(self):
        """Test that empty string raises error."""
        with pytest.raises(ValueError, match="Behavior string cannot be empty"):
            LayoutBinding.from_str("")


class TestLayoutLayer:
    """Test LayoutLayer model."""

    def test_create_layer(self):
        """Test creating layer with bindings."""
        bindings = [
            LayoutBinding.from_str("&kp Q"),
            LayoutBinding.from_str("&kp W"),
        ]
        layer = LayoutLayer(name="test", bindings=bindings)
        assert layer.name == "test"
        assert len(layer.bindings) == 2

    def test_convert_string_bindings(self):
        """Test automatic conversion of string bindings."""
        layer = LayoutLayer(name="test", bindings=["&kp Q", "&kp W"])
        assert len(layer.bindings) == 2
        assert isinstance(layer.bindings[0], LayoutBinding)
        assert layer.bindings[0].value == "&kp"


class TestHoldTapBehavior:
    """Test HoldTapBehavior model."""

    def test_create_hold_tap(self):
        """Test creating hold-tap behavior."""
        ht = HoldTapBehavior(name="test_ht", bindings=["&kp", "&mt"], tapping_term_ms=200, flavor="balanced")
        assert ht.name == "test_ht"
        assert ht.bindings == ["&kp", "&mt"]
        assert ht.tapping_term_ms == 200
        assert ht.flavor == "balanced"

    def test_validate_flavor(self):
        """Test flavor validation."""
        # Valid flavor should pass
        ht = HoldTapBehavior(name="test", bindings=["&kp", "&mt"], flavor="balanced")
        assert ht.flavor == "balanced"

        # Invalid flavor should raise error
        with pytest.raises(ValueError, match="Invalid flavor"):
            HoldTapBehavior(name="test", bindings=["&kp", "&mt"], flavor="invalid")

    def test_validate_bindings_count(self):
        """Test that exactly 2 bindings are required."""
        # Valid: 2 bindings
        ht = HoldTapBehavior(name="test", bindings=["&kp", "&mt"])
        assert len(ht.bindings) == 2

        # Invalid: wrong number of bindings
        with pytest.raises(ValueError, match="exactly 2 bindings"):
            HoldTapBehavior(name="test", bindings=["&kp"])


class TestComboBehavior:
    """Test ComboBehavior model."""

    def test_create_combo(self):
        """Test creating combo behavior."""
        combo = ComboBehavior(name="test_combo", key_positions=[0, 1], binding=LayoutBinding.from_str("&kp ESC"))
        assert combo.name == "test_combo"
        assert combo.key_positions == [0, 1]
        assert combo.binding.value == "&kp"

    def test_validate_key_positions_empty(self):
        """Test that empty key positions raise error."""
        with pytest.raises(ValueError, match="at least one key position"):
            ComboBehavior(name="test", key_positions=[], binding=LayoutBinding.from_str("&kp ESC"))

    def test_validate_key_positions_negative(self):
        """Test that negative key positions raise error."""
        with pytest.raises(ValueError, match="Invalid key position"):
            ComboBehavior(name="test", key_positions=[-1, 0], binding=LayoutBinding.from_str("&kp ESC"))


class TestLayoutData:
    """Test LayoutData model."""

    def test_create_layout_data(self):
        """Test creating complete layout data."""
        data = LayoutData(keyboard="test_keyboard", title="Test Layout", layers=[], hold_taps=[], combos=[])
        assert data.keyboard == "test_keyboard"
        assert data.title == "Test Layout"
        assert isinstance(data.date, datetime)
        assert data.layers == []

    def test_date_serialization(self):
        """Test date serialization to timestamp."""
        data = LayoutData(keyboard="test", title="Test", date=datetime(2023, 1, 1))
        json_data = data.model_dump(mode="json")
        # Should be a timestamp
        assert isinstance(json_data["date"], int)
        assert json_data["date"] == int(datetime(2023, 1, 1).timestamp())

    def test_alias_support(self):
        """Test that aliases work correctly."""
        data = LayoutData(
            keyboard="test",
            title="Test",
            holdTaps=[],  # Using alias
            tapDances=[],  # Using alias
        )
        assert data.hold_taps == []
        assert data.tap_dances == []
