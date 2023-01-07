defmodule Handla.Core.List do
  defstruct ~w[name items timestamp]a

  def new(name) do
    %__MODULE__{
      name: name,
      items: [],
      timestamp: DateTime.utc_now
    }
  end

  def with_items(list, items) do
    %__MODULE__{
      name: list.name,
      items: items,
      timestamp: DateTime.utc_now
    }
  end

  def sort(list) do
    %__MODULE__{
      name: list.name,
      items: Enum.sort_by(list.items, &({&1.category.ordinal,  &2.text}), :asc),
      timestamp: list.timestamp
    }
  end
end
