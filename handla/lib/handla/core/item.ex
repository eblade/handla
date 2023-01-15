defmodule Handla.Core.Item do
  defstruct ~w[text category comment checked timestamp]a

  def new(text, category, comment \\ "", checked \\ false) do
    %__MODULE__{
      text: text,
      category: category,
      comment: comment,
      checked: checked,
      timestamp: DateTime.utc_now
    }
  end

  defp touch(item) do
    %{item | timestamp: DateTime.utc_now}
  end

  def change_text(item, new_text) do
    %{item | text: new_text, timestamp: DateTime.utc_now}
  end

  def change_category(item, new_category) do
    %{item | category: new_category, timestamp: DateTime.utc_now}
  end

  def change_comment(item, new_comment) do
    %{item | comment: new_comment} |> touch
  end

  def remove_comment(item) do
    %{item | comment: "", timestamp: DateTime.utc_now}
  end

  def check(item) do
    %{item | checked: true, timestamp: DateTime.utc_now}
  end

  def uncheck(item) do
    %{item | checked: false} |> touch
  end

  def reset(item) do
    item |> remove_comment |> uncheck
  end

  def equals?(left, right) do
    left.text == right.text && left.category.short == right.category.short
  end
end
